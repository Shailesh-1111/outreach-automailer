def generate_email_html(name, company, role="Full Stack Developer (Backend-Focused)", template_type="formal", sender_name="Shailesh Yadav", sender_exp="1.5+ years", sender_email="shailesh112001y@gmail.com"):
    if not name or name.lower() == 'nan':
        name = "Hiring Manager"
    if not company or company.lower() == 'nan':
        company = "your company"
        
    if template_type == "casual":
        return f"""<b>Subject:</b> Exploring Engineering Roles at {company}<br><br>
Hi {name},<br><br>
I'm <b>{sender_name}</b>, a software engineer with {sender_exp} of experience building high-performance systems. I'm currently looking for new opportunities as a <b>{role}</b> and I've been following the great work your team is doing at {company}.<br><br>
I'm confident I can make an immediate impact and would love to chat if you have any open roles matching my background.<br><br>
Best,<br>
<b>{sender_name}</b><br>
Email: {sender_email}
"""
    elif template_type == "short":
        return f"""<b>Subject:</b> {role} candidate for {company}<br><br>
Hi {name},<br><br>
I'm reaching out to express my interest in joining {company} as a {role}. I have {sender_exp} of experience in backend development and system design.<br><br>
Would love to connect and share my resume if you're actively hiring!<br><br>
Best regards,<br>
<b>{sender_name}</b><br>
Email: {sender_email}
"""
    else: # formal
        return f"""<b>Subject:</b> {sender_name} | Exploring {role} Opportunities at {company}<br><br>
Hi {name},<br><br>
I’m <b>{sender_name}</b>, with strong experience in developing <b>high-performance and scalable systems</b>.<br><br>
<b>Experience:</b> {sender_exp}<br>
<b>Role:</b> {role}<br><br>
With a solid foundation in <b>system design</b>, <b>backend development</b>, and <b>product-focused problem solving</b>, I’m confident in my ability to deliver <b>impactful, business-aligned solutions</b> that contribute meaningfully to <b>{company}’s engineering goals</b>.<br><br>
I’d appreciate the opportunity to connect and explore any openings under your leadership.<br><br>
Best regards,<br>
<b>{sender_name}</b><br>
<b>Email:</b> {sender_email}
"""
