"""
Run this once after the tables are created to pre-load useful DevOps snippets.

Usage:
    python seed_data.py
"""
from database import SessionLocal, engine, Base
from models import Category, Snippet

Base.metadata.create_all(bind=engine)

db = SessionLocal()

SEED_DATA = {
    "Docker": {
        "description": "Container-related commands and tools",
        "snippets": [
            {
                "title": "Build a Docker image",
                "command": "docker build -t myapp:latest .",
                "description": "Builds a Docker image from the Dockerfile in the current directory",
                "tags": ["docker", "build", "image"]
            },
            {
                "title": "Run a container with port mapping",
                "command": "docker run -p 8000:8000 myapp:latest",
                "description": "Runs a container and maps host port 8000 to container port 8000",
                "tags": ["docker", "run", "ports"]
            },
            {
                "title": "List running containers",
                "command": "docker ps",
                "description": "Shows all currently running containers",
                "tags": ["docker", "ps", "list"]
            },
            {
                "title": "View container logs",
                "command": "docker logs -f <container_id>",
                "description": "Streams live logs from a running container",
                "tags": ["docker", "logs", "debug"]
            },
        ]
    },
    "Linux": {
        "description": "Terminal, file system, and process management",
        "snippets": [
            {
                "title": "Check disk usage",
                "command": "df -h",
                "description": "Shows disk space usage in human-readable format",
                "tags": ["linux", "disk", "monitoring"]
            },
            {
                "title": "Find a process by name",
                "command": "ps aux | grep <process_name>",
                "description": "Lists all processes matching a given name",
                "tags": ["linux", "process", "debug"]
            },
            {
                "title": "Change file permissions",
                "command": "chmod 755 script.sh",
                "description": "Makes a file readable/executable by owner, readable by others",
                "tags": ["linux", "permissions", "chmod"]
            },
        ]
    },
    "Git": {
        "description": "Version control commands",
        "snippets": [
            {
                "title": "Undo the last commit (keep changes)",
                "command": "git reset --soft HEAD~1",
                "description": "Removes the last commit but keeps all changes staged",
                "tags": ["git", "reset", "undo"]
            },
            {
                "title": "Create and switch to a new branch",
                "command": "git checkout -b feature/my-feature",
                "description": "Creates a new branch and switches to it in one command",
                "tags": ["git", "branch"]
            },
        ]
    },
    "Terraform": {
        "description": "Infrastructure as Code commands",
        "snippets": [
            {
                "title": "Preview infrastructure changes",
                "command": "terraform plan",
                "description": "Shows what changes Terraform will make without applying them",
                "tags": ["terraform", "plan", "iac"]
            },
            {
                "title": "Apply infrastructure changes",
                "command": "terraform apply -auto-approve",
                "description": "Applies the planned changes without a manual confirmation prompt",
                "tags": ["terraform", "apply", "iac"]
            },
        ]
    },
    "AWS": {
        "description": "AWS CLI commands for ECS, ECR, and general AWS operations",
        "snippets": [
            {
                "title": "Authenticate Docker to ECR",
                "command": "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com",
                "description": "Logs Docker into your private AWS ECR registry",
                "tags": ["aws", "ecr", "docker"]
            },
            {
                "title": "Push image to ECR",
                "command": "docker push <account_id>.dkr.ecr.us-east-1.amazonaws.com/myapp:latest",
                "description": "Pushes a tagged Docker image to your ECR repository",
                "tags": ["aws", "ecr", "push"]
            },
        ]
    }
}


def seed():
    for category_name, data in SEED_DATA.items():
        existing = db.query(Category).filter(Category.name == category_name).first()
        if existing:
            print(f"Skipping '{category_name}' — already exists")
            continue

        category = Category(name=category_name, description=data["description"])
        db.add(category)
        db.commit()
        db.refresh(category)

        for snip in data["snippets"]:
            snippet = Snippet(
                category_id=category.id,
                title=snip["title"],
                command=snip["command"],
                description=snip["description"],
                tags=snip["tags"]
            )
            db.add(snippet)

        db.commit()
        print(f"Seeded category '{category_name}' with {len(data['snippets'])} snippets")

    print("\n✅ Seed data loaded successfully.")


if __name__ == "__main__":
    seed()
    db.close()
