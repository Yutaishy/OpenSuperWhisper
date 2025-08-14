#!/bin/bash
#
# Docker build script with multi-architecture support
# Builds and optionally pushes Docker images

set -e

# Configuration
IMAGE_NAME=${IMAGE_NAME:-opensuperwhisper}
REGISTRY=${REGISTRY:-ghcr.io}
NAMESPACE=${NAMESPACE:-opensuperwhisper}
VERSION=${VERSION:-$(git describe --tags --always 2>/dev/null || echo "dev")}
PLATFORMS=${PLATFORMS:-"linux/amd64,linux/arm64"}
PUSH=${PUSH:-false}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Print banner
echo "========================================="
echo "Docker Multi-Architecture Build"
echo "Image: $REGISTRY/$NAMESPACE/$IMAGE_NAME:$VERSION"
echo "Platforms: $PLATFORMS"
echo "========================================="

# Check Docker buildx
if ! docker buildx version &> /dev/null; then
    echo -e "${RED}Docker buildx is required but not installed${NC}"
    echo "Install Docker Desktop or enable buildx plugin"
    exit 1
fi

# Create/use buildx builder
BUILDER_NAME="opensuperwhisper-builder"
if ! docker buildx ls | grep -q "$BUILDER_NAME"; then
    echo -e "${YELLOW}Creating buildx builder: $BUILDER_NAME${NC}"
    docker buildx create --name "$BUILDER_NAME" --driver docker-container --use
    docker buildx inspect --bootstrap
else
    echo -e "${GREEN}Using existing builder: $BUILDER_NAME${NC}"
    docker buildx use "$BUILDER_NAME"
fi

# Build tags
TAGS=(
    "$REGISTRY/$NAMESPACE/$IMAGE_NAME:$VERSION"
    "$REGISTRY/$NAMESPACE/$IMAGE_NAME:latest"
)

# Add git SHA tag
if GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null); then
    TAGS+=("$REGISTRY/$NAMESPACE/$IMAGE_NAME:sha-$GIT_SHA")
fi

# Build command
BUILD_ARGS=(
    "--platform=$PLATFORMS"
    "--file=Dockerfile"
)

# Add tags
for tag in "${TAGS[@]}"; do
    BUILD_ARGS+=("--tag=$tag")
done

# Cache configuration
BUILD_ARGS+=(
    "--cache-from=type=registry,ref=$REGISTRY/$NAMESPACE/$IMAGE_NAME:buildcache"
    "--cache-to=type=registry,ref=$REGISTRY/$NAMESPACE/$IMAGE_NAME:buildcache,mode=max"
)

# Build metadata
BUILD_ARGS+=(
    "--label=org.opencontainers.image.version=$VERSION"
    "--label=org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    "--label=org.opencontainers.image.revision=$(git rev-parse HEAD 2>/dev/null || echo 'unknown')"
)

# Push or load
if [ "$PUSH" = true ]; then
    BUILD_ARGS+=("--push")
    echo -e "${YELLOW}Will push to registry after build${NC}"
else
    BUILD_ARGS+=("--load")
    echo -e "${YELLOW}Will load to local Docker (single platform only)${NC}"
    
    # When loading, can only build for one platform
    if [[ "$PLATFORMS" == *","* ]]; then
        echo -e "${YELLOW}Multiple platforms specified but --load only supports one${NC}"
        echo -e "${YELLOW}Building for current platform only${NC}"
        BUILD_ARGS[0]="--platform=linux/$(uname -m)"
    fi
fi

# Progress output
BUILD_ARGS+=("--progress=plain")

# Build the image
echo ""
echo -e "${BLUE}Building Docker image...${NC}"
echo "Command: docker buildx build ${BUILD_ARGS[*]} ."
echo ""

if docker buildx build "${BUILD_ARGS[@]}" .; then
    echo ""
    echo -e "${GREEN}✓ Docker build successful!${NC}"
    
    if [ "$PUSH" = true ]; then
        echo ""
        echo "Images pushed to:"
        for tag in "${TAGS[@]}"; do
            echo "  - $tag"
        done
    else
        echo ""
        echo "Image loaded locally as:"
        echo "  - ${TAGS[0]}"
    fi
else
    echo ""
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
fi

# Scan for vulnerabilities (if pushed)
if [ "$PUSH" = true ] && command -v trivy &> /dev/null; then
    echo ""
    echo -e "${BLUE}Scanning image for vulnerabilities...${NC}"
    trivy image --severity HIGH,CRITICAL "${TAGS[0]}" || true
fi

# Generate SBOM (if pushed)
if [ "$PUSH" = true ] && command -v syft &> /dev/null; then
    echo ""
    echo -e "${BLUE}Generating Software Bill of Materials...${NC}"
    syft "${TAGS[0]}" -o spdx-json > "sbom-$VERSION.json"
    echo -e "${GREEN}✓ SBOM saved to sbom-$VERSION.json${NC}"
fi

# Sign image (if pushed and cosign available)
if [ "$PUSH" = true ] && command -v cosign &> /dev/null; then
    echo ""
    echo -e "${BLUE}Signing image...${NC}"
    
    for tag in "${TAGS[@]}"; do
        if cosign sign --yes "$tag"; then
            echo -e "${GREEN}✓ Signed: $tag${NC}"
        else
            echo -e "${YELLOW}⚠ Failed to sign: $tag${NC}"
        fi
    done
fi

echo ""
echo "========================================="
echo -e "${GREEN}Build complete!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
if [ "$PUSH" = false ]; then
    echo "1. Test locally: docker run --rm -p 8000:8000 ${TAGS[0]}"
    echo "2. Push to registry: PUSH=true $0"
else
    echo "1. Deploy: docker pull ${TAGS[0]}"
    echo "2. Run: docker run --rm -p 8000:8000 ${TAGS[0]}"
fi