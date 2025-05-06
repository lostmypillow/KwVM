build_binary() {
    echo "[Step 1] Build binary with pyside6-deploy"
    
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    cd "$PROJECT_ROOT/gui/Python"

    pip install --no-cache-dir -r requirements.txt >/dev/null
    rm -f pysidedeploy.spec
    pyside6-deploy --init
    PATCH_ARGS="--jobs=$(nproc) --include-module=proxmoxer.backends --include-module=proxmoxer.backends.https"
    APP_TITLE="title = 高偉虛擬機"
    sed -i "/^\[nuitka\]/,/^\[/ s|^\(extra_args *= *\)|\1$PATCH_ARGS |" pysidedeploy.spec
    sed -i "/^\[app\]/,/^\[/ s|^title *= *.*|$APP_TITLE|" pysidedeploy.spec
    pyside6-deploy
    cd ../..
    echo ""
}
