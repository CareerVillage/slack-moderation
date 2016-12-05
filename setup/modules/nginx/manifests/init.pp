class nginx() {
  class { "nginx::apt": } ->
  package { "nginx":
    ensure => "present";
  } ->
  class { "nginx::service": }
}
