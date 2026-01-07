# Simple zsh helpers for conda-controlplane

conda-show-solvers() {
  conda-controlplane solvers --format table "$@"
}

conda-show-compilers() {
  conda-controlplane compilers --format table "$@"
}

conda-show-packaging() {
  conda-controlplane packaging --format table "$@"
}

conda-show-network() {
  conda-controlplane network --format table "$@"
}

conda-show-controlplane() {
  conda-controlplane all --format summary "$@"
}
