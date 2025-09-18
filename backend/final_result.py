from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
import json
import requests
from database import get_db
from models import User

router = APIRouter()

# OpenRouter API details
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# ----------------------- Helper Functions -----------------------

def get_user_data(username: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def extract_test_results(user):
    gap_analysis = json.loads(user.gap_analysis) if user.gap_analysis else {}
    technical_test = json.loads(user.technical_test) if user.technical_test else {}
    non_technical_test = user.non_technical_test if user.non_technical_test else "Unknown"

    average_elo = gap_analysis.get("average_elo", 0)
    solved = technical_test.get("solved", 0)
    milestone = technical_test.get("milestone", "0")

    try:
        milestone_number = int(milestone.split()[0])
    except (ValueError, IndexError):
        milestone_number = 0
    
    technical_test_combined = f"{solved},{milestone_number}"
    return average_elo, technical_test_combined, non_technical_test, solved, milestone_number

def determine_skill_level(solved, milestone_number):
    if solved == 0:
        return "beginner"
    elif solved == milestone_number:
        return "basic"
    elif solved > milestone_number:
        return "advanced" if solved > milestone_number + 5 else "adept"
    return "beginner"

def generate_career_prompt(average_elo, non_technical_test, skill_level):
    return (
        f"I am focused on building a strong career in programming and want a clear, no-nonsense roadmap to get there.\n\n"
        f"My current coding proficiency is rated at {average_elo} (on a scale of 800 to 1600). **1200 is the absolute minimum to be considered a competent developer.**\n"
        f"If my rating is below 1200, that means my foundational knowledge is weak, and I need a structured plan to fix it fast.\n"
        f"My personality type is '{non_technical_test}', which affects how I learn and solve problems.\n"
        f"I identify as a {skill_level} programmer, and I want a direct path to leveling up my skills.\n\n"
        
        "Provide a **highly detailed, structured career roadmap** that includes:\n"
        
        "### **1. Core Programming Languages & Technologies**\n"
        "- What are the most relevant languages and technologies I should master?\n"
        "- Rank them by priority based on my skill level.\n"
        "- Explain why these technologies are important.\n"
        "- Provide links to official documentation and the best learning resources.\n\n"

        "### **2. Best Learning Strategies**\n"
        "- Given my personality type, what are the most effective ways for me to improve?\n"
        "- Should I focus on structured courses, hands-on projects, competitive programming, or another method?\n"
        "- Break this down into daily, weekly, and monthly habits.\n"
        "- Include tips on how to stay consistent and avoid burnout.\n\n"

        "### **3. Career Paths That Match My Strengths**\n"
        "- What are the most suitable career paths for me?\n"
        "- Rank the best options from entry-level to advanced career tracks.\n"
        "- Explain what skills and experience are required for each role.\n"
        "- Include links to job descriptions and industry trends.\n\n"

        "### **4. Critical Mistakes to Avoid**\n"
        "- What are the most common mistakes developers make at my level?\n"
        "- Provide real-world examples of these mistakes and how to fix them.\n"
        "- Offer practical advice on debugging, best practices, and career pitfalls.\n\n"

        "### **5. Best Resources to Learn From**\n"
        "- Recommend the top courses, books, and platforms for learning.\n"
        "- Break them down by topic (e.g., frontend, backend, algorithms, DevOps, etc.).\n"
        "- Prioritize free and high-quality resources.\n\n"

        "### **6. Milestones & Benchmarks**\n"
        "- Define clear checkpoints I should hit to track my progress.\n"
        "- What should I be able to build or understand after 1 month, 3 months, 6 months, and 1 year?\n"
        "- Provide coding challenges, mini-projects, and real-world tasks to validate my skills.\n\n"

        "### **7. Career Roadmaps from Roadmap.sh**\n"
        "Find the most **relevant career roadmap** for my situation from the list below and include a direct link in your response:\n\n"

        "**Role-based Roadmaps:**\n"
        "- 🔗 [Frontend Developer](https://roadmap.sh/frontend)\n"
        "- 🔗 [Backend Developer](https://roadmap.sh/backend)\n"
        "- 🔗 [DevOps Engineer](https://roadmap.sh/devops)\n"
        "- 🔗 [Full Stack Developer](https://roadmap.sh/fullstack)\n"
        "- 🔗 [AI Engineer](https://roadmap.sh/ai)\n"
        "- 🔗 [Data Analyst](https://roadmap.sh/data-analyst)\n"
        "- 🔗 [AI and Data Scientist](https://roadmap.sh/ai-and-data-scientist)\n"
        "- 🔗 [Android Developer](https://roadmap.sh/android)\n"
        "- 🔗 [iOS Developer](https://roadmap.sh/ios)\n"
        "- 🔗 [PostgreSQL Developer](https://roadmap.sh/postgresql)\n"
        "- 🔗 [Blockchain Developer](https://roadmap.sh/blockchain)\n"
        "- 🔗 [QA Engineer](https://roadmap.sh/qa)\n"
        "- 🔗 [Software Architect](https://roadmap.sh/software-architect)\n"
        "- 🔗 [Cyber Security Specialist](https://roadmap.sh/cyber-security)\n"
        "- 🔗 [UX Designer](https://roadmap.sh/ux)\n"
        "- 🔗 [Game Developer](https://roadmap.sh/game-developer)\n"
        "- 🔗 [Technical Writer](https://roadmap.sh/technical-writer)\n"
        "- 🔗 [MLOps Engineer](https://roadmap.sh/mlops)\n"
        "- 🔗 [Product Manager](https://roadmap.sh/product-manager)\n"
        "- 🔗 [Engineering Manager](https://roadmap.sh/engineering-manager)\n"
        "- 🔗 [Developer Relations Specialist](https://roadmap.sh/developer-relations)\n\n"

        "**Skill-based Roadmaps:**\n"
        "- 🔗 [Computer Science](https://roadmap.sh/computer-science)\n"
        "- 🔗 [React Developer](https://roadmap.sh/react)\n"
        "- 🔗 [Vue Developer](https://roadmap.sh/vue)\n"
        "- 🔗 [Angular Developer](https://roadmap.sh/angular)\n"
        "- 🔗 [JavaScript Developer](https://roadmap.sh/javascript)\n"
        "- 🔗 [Node.js Developer](https://roadmap.sh/nodejs)\n"
        "- 🔗 [TypeScript Developer](https://roadmap.sh/typescript)\n"
        "- 🔗 [Python Developer](https://roadmap.sh/python)\n"
        "- 🔗 [SQL Developer](https://roadmap.sh/sql)\n"
        "- 🔗 [System Design](https://roadmap.sh/system-design)\n"
        "- 🔗 [API Design](https://roadmap.sh/api-design)\n"
        "- 🔗 [ASP.NET Core Developer](https://roadmap.sh/aspnet-core)\n"
        "- 🔗 [Java Developer](https://roadmap.sh/java)\n"
        "- 🔗 [C++ Developer](https://roadmap.sh/cpp)\n"
        "- 🔗 [Flutter Developer](https://roadmap.sh/flutter)\n"
        "- 🔗 [Spring Boot Developer](https://roadmap.sh/spring-boot)\n"
        "- 🔗 [Go Developer](https://roadmap.sh/go)\n"
        "- 🔗 [Rust Developer](https://roadmap.sh/rust)\n"
        "- 🔗 [GraphQL Developer](https://roadmap.sh/graphql)\n"
        "- 🔗 [Design and Architecture](https://roadmap.sh/design-and-architecture)\n"
        "- 🔗 [Design System](https://roadmap.sh/design-system)\n"
        "- 🔗 [React Native Developer](https://roadmap.sh/react-native)\n"
        "- 🔗 [AWS Developer](https://roadmap.sh/aws)\n"
        "- 🔗 [Code Review](https://roadmap.sh/code-review)\n"
        "- 🔗 [Docker](https://roadmap.sh/docker)\n"
        "- 🔗 [Kubernetes](https://roadmap.sh/kubernetes)\n"
        "- 🔗 [Linux](https://roadmap.sh/linux)\n"
        "- 🔗 [MongoDB Developer](https://roadmap.sh/mongodb)\n"
        "- 🔗 [Prompt Engineering](https://roadmap.sh/prompt-engineering)\n"
        "- 🔗 [Terraform](https://roadmap.sh/terraform)\n"
        "- 🔗 [Data Structures & Algorithms](https://roadmap.sh/data-structures)\n"
        "- 🔗 [Git and GitHub](https://roadmap.sh/git)\n"
        "- 🔗 [Redis Developer](https://roadmap.sh/redis)\n"
        "- 🔗 [PHP Developer](https://roadmap.sh/php)\n"
        "- 🔗 [Cloudflare](https://roadmap.sh/cloudflare)\n\n"

        "### **Final Instructions:**\n"
        "- Ensure the report is as detailed as possible.\n"
        "- Provide in-depth explanations and **real-world examples** where applicable.\n"
        "- Include step-by-step plans, industry trends, and direct action points.\n"
        "- If multiple roadmaps apply, rank them and justify your choice.\n"
    )

def call_ai_api(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    else:
        raise HTTPException(status_code=500, detail=f"Error from AI API: {response.text}")

# ----------------------- Main Endpoints -----------------------

@router.post("/generate_final_result/{username}")
def generate_final_result(username: str, db: Session = Depends(get_db)):
    user = get_user_data(username, db)
    average_elo, technical_test_combined, non_technical_test, solved, milestone_number = extract_test_results(user)
    
    skill_level = determine_skill_level(solved, milestone_number)
    prompt = generate_career_prompt(average_elo, non_technical_test, skill_level)
    career_guidance = call_ai_api(prompt)
    
    final_result_data = {
        "average_elo": average_elo,
        "technical_test": technical_test_combined,
        "non_technical_test": non_technical_test,
        "career_guidance": career_guidance
    }

    print("Final result before saving:", final_result_data)  # Debugging

    # Convert JSON to string explicitly before saving
    user.final_result = json.dumps(final_result_data)

    # Mark as modified for SQLAlchemy
    flag_modified(user, "final_result")
    db.commit()
    db.refresh(user)

    print("Final result saved in database:", user.final_result)  # Debugging

    return {"message": "Final result generated successfully", "final_result": final_result_data}

@router.get("/get_final_result/{username}")
def get_final_result(username: str, db: Session = Depends(get_db)):
    user = get_user_data(username, db)
    if not user.final_result:
        raise HTTPException(status_code=404, detail="Final result not found")
    return json.loads(user.final_result)
