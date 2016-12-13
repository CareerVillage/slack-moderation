class moderation::venv {

    if $moderation::target != 'dev' {
        include moderation::code
    }

    if $moderation::target == 'dev' {
        $settings = 'local'
    } elsif $moderation::target == 'pro' {
        $settings = 'production'
    } elsif $moderation::target == 'sta' {
        $settings = 'staging'
    } elsif $moderation::target == 'test' {
        $settings = 'test'
    } else {
        $settings = 'local'
    }

    python::venv { $moderation::venv_dir:
        requirements => "${moderation::source_dir}/requirements/${settings}.pip",
        user         => $moderation::user,
        group        => $moderation::group,
        require      => [Class["moderation"]];
    }

}