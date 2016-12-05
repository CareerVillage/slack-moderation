class moderation::app::db () {

    include moderation::db

    postgresql::database { "moderation":
      charset => "utf8",
      owner   => "moderation",
      require => Class["moderation::db"];
    }

    postgresql::database_grant { "moderation-all":
        privilege => "ALL",
        db => "moderation",
        role => "moderation",
        require   => Postgresql::Database["moderation"];
    }

    postgresql::database_grant { "moderation-connect":
        privilege => "CONNECT",
        db => "moderation",
        role => "moderation",
        require   => Postgresql::Database["moderation"];
    }
    
}