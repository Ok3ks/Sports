provider "google" {
    region = var.region
}

module "container_vms" {
    source = "terraform-google-modules/vm/google"
    version = "10.1.1"
}

module "sqldb" {
    source = "GoogleCloudPlatform/sql-db/google//examples/mysql-public"
    version = "18.2.0"
    project_id = var.project_id
    db_name = var.db_name
}