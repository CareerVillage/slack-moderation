class locales (
  $available      = $::locales::params::available,
  $default_value  = $::locales::params::default_value,
  $localegenfile  = $::locales::params::localegenfile,
  $package_ensure = $::locales::params::package_ensure,
  $package_name   = $::locales::params::package_name,
) inherits locales::params {
  validate_array($available)
  validate_string(
    $default_value,
    $package_ensure,
    $package_name
  )
  validate_absolute_path($localegenfile)

  anchor { 'locales::begin': }  ->
  class { 'locales::install': }  ->
  class { 'locales::config': }   ->
  anchor { 'locales::end': }
}
