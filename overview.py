from diagrams import Diagram
from diagrams.c4 import Person, Container, Database, System, SystemBoundary, Relationship
from diagrams.firebase.develop import Authentication, Firestore
from diagrams.gcp.compute import Run
from diagrams import Cluster
if __name__ == "__main__":
    with Diagram("FPL Analytic Tool", show =True):
            with Cluster("Cloudflare hosted website"):
                user = Container(name="User visits", type="")

            with Cluster("Frontend built in Flutter"):
                    onboarding_page = Container(
                    name = "Onboarding Page",
                    type="",
                    description="Request New user data for personalisation"
                    )
                    login_page = Container(
                        name = "Login Page",
                        type="",
                        description="Handles user authentication into the website"
                    )
                    user_report_page = Container(
                        name = "User/League/Personal Page",
                        type="",
                        description="Receives Query from User"
                    )

            auth = Authentication(label="Firebase Auth")

            with Cluster(""):
                user_db = Firestore(label="User info store")


            with Cluster("Deployment"):
                with Cluster("GCP CloudRun"):
                    container_run = Run(label="Backend Deployment Environment")
                    with Cluster("Docker Container storing backend Python Code"):
                        backend = Container(
                            name="backend services",
                            technology="Django",
                            description="Executes Data Analysis process",
                            )
                        database = Container(
                            name="Database",
                            description="In-Session Database",
                            type = ""
                            )
                        startup_script = Container(
                            name="startup shell script",
                            description="populates database with data from 3rd-party API",
                            type=""
                        )
                    
                
                     

            auth << login_page
            onboarding_page >> login_page 
            onboarding_page >> user_db 
            auth >> user_report_page

            container_run >> login_page
            login_page >> container_run

            user_report_page >> backend
            backend >> database >> backend
            startup_script >> database
            backend >> user_db >> login_page 
            
            user >> onboarding_page

            

           
            
        