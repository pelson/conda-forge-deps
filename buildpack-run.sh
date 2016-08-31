#!/usr/bin/env bash
set -x

STORAGE_LOCN=$(pwd)

# ----------

mkdir -p "$1" "$2" "$3"
build=$(cd "$1/" && pwd)
cache=$(cd "$2/" && pwd)
env_dir=$(cd "$3/" && pwd)

# -------

# Secret variables aren't exported in the build phase, but they are available
# from the environment directory.
export "GH_TOKEN=$(cat $env_dir/GH_TOKEN)"

# -------

# Install vim
mkdir $STORAGE_LOCN/.vim
curl https://s3.amazonaws.com/heroku-vim/vim-7.3.tar.gz --location --silent | tar xz -C $STORAGE_LOCN/.vim

# Configure vim

cat <<-'EOF' > ${STORAGE_LOCN}/.vimrc
    set backspace=indent,eol,start
    set ruler
    set hls
    filetype indent on

    set tabstop=4
    set shiftwidth=4
    set expandtab

    set viminfo='10,\"100,:20,%,n~/.viminfo

    if has("autocmd")
           au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif
    endif
EOF

# ---------

# Run whenever the dyno starts-up!

cp -rf ${BUILD_DIR}/compute_dependencies.py ${STORAGE_LOCN}/


# ----------

wget -q https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/.conda
$HOME/.conda/bin/conda install -c conda-forge --yes conda-execute conda-smithy conda-build python=3 tornado

cp -rf $HOME/.conda $STORAGE_LOCN/.conda

mkdir -p $build/.profile.d
cat <<-'EOF' > $build/.profile.d/conda.sh
    # append to path variable
    export PATH=$HOME/.conda/bin:$PATH
    export PATH=$HOME/.vim/bin:$PATH

    # set default encoding to UTF-8
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8  

    export CONDA_NPY=110

    # Compute the dependencies each time the process starts up.
    python ~/compute_dependencies.py --feedstocks-dir ./feedstocks
EOF


cat <<-'EOF' > ${STORAGE_LOCN}/.condarc
    channels:
      - conda-forge
      - defaults
    show_channel_urls: true
    add_pip_as_python_dependency: false
EOF

# -------
mkdir -p $STORAGE_LOCN/.conda-smithy
ln -s $STORAGE_LOCN/.conda-smithy $HOME/.conda-smithy
echo $GH_TOKEN > ~/.conda-smithy/github.token

mkdir -p $STORAGE_LOCN/feedstocks

$HOME/.conda/bin/feedstocks clone --feedstocks-dir $STORAGE_LOCN/feedstocks

# -------

