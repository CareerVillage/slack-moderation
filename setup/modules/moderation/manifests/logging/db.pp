class moderation::logging::db {

    include moderation::db

    postgresql::database { "logging":
      charset => "utf8",
      require => Class["moderation::db"];
    }

    postgresql::database_grant { "logging-all":
        privilege => "ALL",
        db        => "logging",
        role      => "moderation",
        require   => Postgresql::Database["logging"];
    }

    postgresql::database_grant { "logging-connect":
        privilege => "CONNECT",
        db        => "logging",
        role      => "moderation",
        require   => Postgresql::Database["logging"];
    }

}