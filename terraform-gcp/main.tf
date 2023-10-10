terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "4.51.0"
        }
    }
}

provider "google" {
    credentials = file ('keys/bets-project-401114-a51cd531202e.json')
    project = "bets-project-401114"
    region = ""
    zone = ""
}

resource "google_sql_database_instance" "mysql_pvp_instance_name" {
    name = "id2team"
    region = "europe-west2"
    database_version = "MYSQL_8_0"
    root_password = "?*y{ceIA&ThGQ0G_"
    settings {
        tier = "db-f1-micro"
    }
}
}