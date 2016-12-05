class master {

    $target = $::moderation_target
    $root_dir = "/home/moderation/moderation"
    $user = "moderation"
    $group = "moderation"

    host {
        "moderation.moderation.db":
            ip => $::moderation_moderation_db_address;
        "moderation.moderation.cache":
            ip => $::moderation_moderation_cache_address;
    }

    class { "moderation":
        target => $target,
        root_dir => $root_dir,
        user => $user,
        group => $group;
    }

    class { "moderation::app::db": }

    class { "moderation::app::site":
        role => "master";
    }

    class { "moderation::app::deploy":
        role => "master";
    }

    class { "moderation::rabbitmq": }

    class { "moderation::cache": }

}

class { "master": }
