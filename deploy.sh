#!/bin/zsh

# Change to your project's directory
cd /Users/blakeurmos/Documents/GitHub/caloriecounter

source env/bin/activate
pip freeze > requirements.txt

# Add all new and changed files to git
git add .

# Prompt for a commit message
echo "Enter the commit message: "
read commit_message

# Commit the changes with the user's input as the commit message
git commit -m "$commit_message"

# Push the changes to GitHub
git push origin main

# Wait for Enter key press to proceed
echo "Press Enter to proceed with the deployment..."
read

# SSH to the EC2 server and run the deployment script
ssh -i "/Users/blakeurmos/Documents/GitHub/lowvoltagenation/lowvoltagenation.pem" ubuntu@ec2-52-54-98-87.compute-1.amazonaws.com 'bash /var/www/deploy-caloriecounter.sh'