define nginx::upstream ($name, $source) {
  File {
    owner => "root",
    group => "root",
    mode => "0644"
  }
  file { "/etc/nginx/conf.d/${name}-upstream.conf":
    ensure => "file",
    source => $source,
    notify => Class['nginx::service'];
  }
}
