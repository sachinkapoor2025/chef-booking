#!/usr/bin/env python3
"""
Blog Submission Handler for Maharaja Chef Services
Handles blog post submissions and approval workflow
"""

import json
import os
import datetime
from pathlib import Path

class BlogSubmissionHandler:
    def __init__(self):
        self.submissions_dir = Path("backend/submissions")
        self.submissions_dir.mkdir(exist_ok=True)
        
    def submit_blog(self, blog_data):
        """
        Handle blog submission
        """
        try:
            # Generate unique submission ID
            submission_id = f"blog_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Add metadata
            submission_data = {
                "submission_id": submission_id,
                "status": "pending_review",
                "submitted_at": datetime.datetime.now().isoformat(),
                "approved_at": None,
                "data": blog_data
            }
            
            # Save submission
            submission_file = self.submissions_dir / f"{submission_id}.json"
            with open(submission_file, 'w') as f:
                json.dump(submission_data, f, indent=2)
            
            return {
                "success": True,
                "message": "Blog submission received successfully",
                "submission_id": submission_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error submitting blog: {str(e)}"
            }
    
    def get_submissions(self, status=None):
        """
        Get all submissions, optionally filtered by status
        """
        submissions = []
        
        for file_path in self.submissions_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    submission = json.load(f)
                    if status is None or submission.get("status") == status:
                        submissions.append(submission)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        # Sort by submission date
        submissions.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
        return submissions
    
    def approve_submission(self, submission_id):
        """
        Approve a blog submission
        """
        submission_file = self.submissions_dir / f"{submission_id}.json"
        
        if not submission_file.exists():
            return {"success": False, "message": "Submission not found"}
        
        try:
            with open(submission_file, 'r') as f:
                submission = json.load(f)
            
            submission["status"] = "approved"
            submission["approved_at"] = datetime.datetime.now().isoformat()
            
            with open(submission_file, 'w') as f:
                json.dump(submission, f, indent=2)
            
            # Generate blog HTML file
            self._generate_blog_html(submission)
            
            return {"success": True, "message": "Blog approved and published"}
            
        except Exception as e:
            return {"success": False, "message": f"Error approving submission: {str(e)}"}
    
    def reject_submission(self, submission_id, reason=None):
        """
        Reject a blog submission
        """
        submission_file = self.submissions_dir / f"{submission_id}.json"
        
        if not submission_file.exists():
            return {"success": False, "message": "Submission not found"}
        
        try:
            with open(submission_file, 'r') as f:
                submission = json.load(f)
            
            submission["status"] = "rejected"
            submission["rejection_reason"] = reason
            submission["rejected_at"] = datetime.datetime.now().isoformat()
            
            with open(submission_file, 'w') as f:
                json.dump(submission, f, indent=2)
            
            return {"success": True, "message": "Blog submission rejected"}
            
        except Exception as e:
            return {"success": False, "message": f"Error rejecting submission: {str(e)}"}
    
    def _generate_blog_html(self, submission):
        """
        Generate HTML file for approved blog
        """
        blog_data = submission["data"]
        
        # Generate filename from title
        title_slug = blog_data["blogTitle"].lower().replace(" ", "-").replace("/", "-")
        filename = f"website/blog-{title_slug}.html"
        
        html_content = self._create_blog_template(blog_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _create_blog_template(self, blog_data):
        """
        Create HTML template for blog post
        """
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{blog_data["blogTitle"]} - Maharaja Chef Services</title>
    <meta name="description" content="{blog_data.get("blogSummary", "")}">
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* Blog Post Styles */
        .blog-post-container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-top: 2rem;
            margin-bottom: 2rem;
        }}

        .blog-header {{
            text-align: center;
            margin-bottom: 2rem;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 2rem;
        }}

        .blog-title {{
            font-size: 2.5rem;
            color: #1e3a8a;
            margin-bottom: 1rem;
            font-weight: 700;
        }}

        .blog-meta {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }}

        .blog-meta span {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .blog-content {{
            line-height: 1.8;
            color: #333;
            font-size: 1.1rem;
        }}

        .blog-content h2 {{
            color: #1e3a8a;
            margin-top: 2rem;
            margin-bottom: 1rem;
            font-size: 1.8rem;
            border-left: 4px solid #3b82f6;
            padding-left: 1rem;
        }}

        .blog-content h3 {{
            color: #3b82f6;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            font-size: 1.4rem;
        }}

        .blog-content p {{
            margin-bottom: 1.5rem;
        }}

        .author-box {{
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            padding: 1.5rem;
            border-radius: 12px;
            margin-top: 2rem;
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }}

        .author-avatar {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: #3b82f6;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 2rem;
        }}

        .author-info h4 {{
            margin: 0 0 0.5rem 0;
            color: #1e3a8a;
        }}

        .author-info p {{
            margin: 0;
            color: #64748b;
        }}

        .blog-actions {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 2px solid #e5e7eb;
        }}

        .btn-secondary {{
            background: #3b82f6;
            color: white;
            padding: 0.75rem 2rem;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .btn-secondary:hover {{
            background: #1d4ed8;
            transform: translateY(-2px);
        }}

        .btn-outline {{
            background: transparent;
            color: #3b82f6;
            border: 2px solid #3b82f6;
            padding: 0.75rem 2rem;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .btn-outline:hover {{
            background: #3b82f6;
            color: white;
        }}

        @media (max-width: 768px) {{
            .blog-post-container {{
                padding: 1rem;
                margin: 1rem;
            }}
            
            .blog-title {{
                font-size: 2rem;
            }}
            
            .blog-meta {{
                flex-direction: column;
                gap: 1rem;
            }}
            
            .author-box {{
                flex-direction: column;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <main>
        <section id="blog-post">
            <div class="blog-post-container">
                <div class="blog-header">
                    <h1 class="blog-title">{blog_data["blogTitle"]}</h1>
                    <div class="blog-meta">
                        <span><i class="fas fa-calendar"></i> {datetime.datetime.now().strftime("%B %d, %Y")}</span>
                        <span><i class="fas fa-user-chef"></i> By {blog_data["fullName"]}</span>
                        <span><i class="fas fa-clock"></i> {len(blog_data["blogContent"].split()) // 200} min read</span>
                        <span><i class="fas fa-tag"></i> {blog_data["blogCategory"]}</span>
                    </div>
                </div>

                <div class="blog-content">
                    <p><strong>{blog_data["blogSummary"]}</strong></p>
                    <p>{blog_data["blogContent"]}</p>
                </div>

                <div class="author-box">
                    <div class="author-avatar">
                        <i class="fas fa-user-chef"></i>
                    </div>
                    <div class="author-info">
                        <h4>{blog_data["fullName"]}</h4>
                        <p>{blog_data.get("profession", "Guest Author")}</p>
                        <p>Email: {blog_data["email"]}</p>
                    </div>
                </div>

                <div class="blog-actions">
                    <a href="blogs.html" class="btn-secondary">
                        <i class="fas fa-arrow-left"></i> Back to Blogs
                    </a>
                    <a href="submit-blog.html" class="btn-outline">
                        <i class="fas fa-pen"></i> Submit Your Blog
                    </a>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="footer-content">
            <div class="footer-column">
                <h3>Maharaja Chef Services</h3>
                <p>Premium personal chef services across the USA. Bringing restaurant-quality dining to your home.</p>
            </div>
            <div class="footer-column">
                <h3>Quick Links</h3>
                <ul>
                    <li><a href="index.html">Home</a></li>
                    <li><a href="chef-services.html">Services</a></li>
                    <li><a href="explore-chefs.html">Explore Chefs</a></li>
                    <li><a href="gallery.html">Gallery</a></li>
                </ul>
            </div>
            <div class="footer-column">
                <h3>Legal</h3>
                <ul>
                    <li><a href="terms-conditions.html">Terms & Conditions</a></li>
                    <li><a href="privacy-policy.html">Privacy Policy</a></li>
                    <li><a href="refund-policy.html">Refund Policy</a></li>
                </ul>
            </div>
            <div class="footer-column">
                <h3>Contact Us</h3>
                <div class="contact-info" style="color: #333;">
                    <p><i class="fas fa-phone"></i> 408-690-1610</p>
                    <p><i class="fas fa-envelope"></i> info@maharajachef.com</p>
                </div>
                <div class="social-media">
                    <a href="https://facebook.com" target="_blank" aria-label="Facebook"><i class="fab fa-facebook-f"></i></a>
                    <a href="https://www.instagram.com/maharajachef/?hl=en" target="_blank" aria-label="Instagram"><i class="fab fa-instagram"></i></a>
                    <a href="https://twitter.com" target="_blank" aria-label="Twitter"><i class="fab fa-twitter"></i></a>
                </div>
            </div>
        </div>
        <hr>
        <div class="footer-bottom">
            <p>&copy; 2024 Maharaja Chef Services. All rights reserved.</p>
        </div>
    </footer>

    <script src="js/script.js"></script>
    <script src="js/global-header.js"></script>
</body>
</html>'''

if __name__ == "__main__":
    # Example usage
    handler = BlogSubmissionHandler()
    
    # Example blog data
    example_blog = {
        "fullName": "Jane Doe",
        "email": "jane@example.com",
        "phone": "(555) 123-4567",
        "profession": "Professional Chef",
        "blogTitle": "Example Blog Post",
        "blogCategory": "Cooking Techniques",
        "blogContent": "This is an example blog post content...",
        "blogSummary": "This is an example summary.",
        "termsAgreement": True
    }
    
    result = handler.submit_blog(example_blog)
    print(result)