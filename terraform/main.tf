provider "aws" {
    region = var.region

}

module "container_vms" {
    source = "terraform-google-modules/vm/google"
    version = "10.1.1"

    project_id = var.project_id
    subnetwork = var.subnetwork
    zone = var.zone
}

module "sqldb" {
    source = "GoogleCloudPlatform/sql-db/google//examples/postgresql-public"
    version = "18.2.0"
    project_id = var.project_id
    db_name = var.db_name
}

resource google_compute_engine{

}

resource google_container_registry{

}

resource cloud_google_sql{


}

resource google_cloud_memorystore {

}