from diagrams import Diagram
from diagrams.c4 import Person, Container, Database, System, SystemBoundary, Relationship
from diagrams.firebase.develop import Authentication, Firestore
from diagrams.gcp.compute import Run
from diagrams.gcp.database import Memorystore, SQL
from diagrams import Cluster
if __name__ == "__main__":
    with Diagram("FPL Analytic Tool", show =True, filename="monolith"):
        with Cluster("Cloudflare hosted website"):
            user = Container(name="User visits", type="")

        with Cluster(""):
                user_db = Firestore(label="User info store")

        with Cluster("Frontend Deployed on Firebase"):
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
        user_report_page >> container_run

        user_report_page >> backend
        backend >> database >> backend
        startup_script >> database
        backend >> user_db >> user_report_page 
        
        user >> onboarding_page


    with Diagram("FPL Analytic Tool", show =True, filename="decoupled"):
        with Cluster("Cloudflare hosted website"):
            user = Container(name="User visits", type="")


        with Cluster("Frontend Deployed on Firebase"):
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
            container_run = Run(label="Backend Deployment Environment")
            with Cluster("Docker Container storing backend Python Code"):
                backend = Container(
                    name="backend services",
                    description="Executes Data Analysis process \n \n (Framework: Pandas, Django, SqlAlchemy, Ariadne GraphQL)",
                    type=""
                    )
                
            user_db = Memorystore(label="User info redis store")

            database = SQL(label="Postgres Database"
                    )
                    
                
                     

        auth << login_page << auth
        onboarding_page >> login_page 
        onboarding_page >> user_db
        login_page >> user_report_page

        container_run >> login_page
        user_report_page >> container_run

        user_report_page >> backend
        backend >> database
        database >> backend
        backend >> user_db >> user_report_page 
        
        user >> onboarding_page

            

           
            
        