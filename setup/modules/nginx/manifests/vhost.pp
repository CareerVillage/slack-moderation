define nginx::vhost ( $name, $source = undef, $content = undef ) {
  File {
    owner => "root",
    group => "root",
    mode => "0644"
  }
  file { "/etc/nginx/conf.d/${name}.conf":
    ensure => "file",
    source => $source,
    notify => Service["nginx"],
    content => $content;
  }
}
