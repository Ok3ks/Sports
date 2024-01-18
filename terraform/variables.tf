
variable "region" {
    description = "Region" 
    type = string
    default = "europe-west2"
}

variable "subnetwork" {
    description = "Subnetwork"
    type = string 
    default = "10.154.0.2"
}

variable "zone" {
    description = "Zone"
    type = string 
    default = "europe-west2-b"
}

variable "project_id" {
    description = "Project name"
    type = string 
    default = "fpl-analysis-tool"
}

variable "db_name" {
    description = "Name of the db"
    type = string 
    default = "fpl"
}

variable "repo_name" {
    description = "Name of repo"
    type = string 
    default = "images"
}