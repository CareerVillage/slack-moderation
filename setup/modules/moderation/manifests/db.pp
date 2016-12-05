class moderation::db {

    class { "postgresql::server":
        config_hash => {
            "ip_mask_deny_postgres_user" => "0.0.0.0/32",
            "ip_mask_allow_all_users" => "0.0.0.0/0",
            "listen_addresses"  => "*",
            "manage_redhat_firewall" => true,
            "postgres_password" => "postgres"
        };
    }

    postgresql::database_user { "moderation":
        password_hash => postgresql_password("moderation", "moderation"),
        createdb      => true,
        require       => Class["postgresql::server"];
    }

}