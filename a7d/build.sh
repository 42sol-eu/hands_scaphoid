set -e 
_a7d/activate_venv.sh

uv version --bump patch
uv build 

VERSION=$(uv version --short)
echo "Built version: $VERSION"
cp "dist/hands_scaphoid-$VERSION-py3-none-any.whl" "../hands_scaphoid/tests/" 2>/dev/null || echo "Warning: Could not copy to hands_scaphoid/tests/"
echo "Build complete for hands_scaphoid"