def generate_email_html(name, company, role="SDE", template_type="t1", sender_name="Shailesh Yadav", sender_exp="2+ years", sender_email="shailesh112001y@gmail.com"):
    if not name or name.lower() == 'nan':
        name = "Hiring Manager"
    if not company or company.lower() == 'nan':
        company = "your organization"
        
    html = ""
    if template_type == "t1":
        html = f"""Hi {name},<br><br>
I’m {sender_name}, an IIT BHU’24 grad and SDE with {sender_exp} of experience in scalable systems, full-stack, and AI/LLM tools (currently at Eduvanz Financing).<br><br>
I'm exploring {role} opportunities at {company} and would love to connect. I’ve attached my resume for your reference.<br><br>
Best,<br>
{sender_name}<br>
+917355603902
"""
    elif template_type == "t2":
        html = f"""Hi {name},<br><br>
I am an SDE with {sender_exp} of experience building scalable, real-time, and AI/LLM-powered systems (Java, Python, React) at Eduvanz Financing.<br><br>
As an IIT BHU’24 graduate, I admire the work happening at {company} and am currently looking for new {role} roles. I’ve attached my resume—would love to chat if there's a fit!<br><br>
Best regards,<br>
{sender_name}<br>
+917355603902
"""
    elif template_type == "t3":
        html = f"""Hi {name},<br><br>
I’m reaching out to express my interest in {role} roles at {company}. I bring {sender_exp} of full-stack and AI development experience from Eduvanz Financing, backed by a degree from IIT BHU ('24).<br><br>
My stack includes Java, Python, React, and VectorDBs. Please find my resume attached. Looking forward to connecting!<br><br>
Thanks,<br>
{sender_name}<br>
+917355603902
"""
    elif template_type == "t4":
        html = f"""Hi {name},<br><br>
I’m an SDE (IIT BHU’24) specializing in Java, Python, React, and LLM implementations. With {sender_exp} of hands-on experience at Eduvanz Financing, I'm now exploring open {role} opportunities at {company}.<br><br>
I’ve attached my resume outlining my recent work with scalable applications. Let me know if you have any openings that align!<br><br>
Best,<br>
{sender_name}<br>
+917355603902
"""
    elif template_type == "t5":
        html = f"""Hi {name},<br><br>
Hope you're having a great week!<br><br>
I’m {sender_name}, an IIT BHU'24 alum with {sender_exp} of SDE experience building scalable full-stack and AI-driven solutions. I’d love to bring my expertise to the engineering team at {company}.<br><br>
My resume is attached for your review. Would be grateful for a quick chat if there are any suitable openings.<br><br>
Best,<br>
{sender_name}<br>
+917355603902
"""
    elif template_type == "t6":
        html = f"""Hi {name},<br><br>
I’m {sender_name}, an IIT BHU’24 graduate with {sender_exp} of experience as an SDE at Eduvanz Financing Pvt. Ltd.<br><br>
I'm exploring {role} opportunities at {company} and would love to connect. My experience has primarily been in scalable systems, full stack, real-time applications, and AI/LLM-powered systems and tools.<br><br>
Experience: {sender_exp}<br>
Current Company: Eduvanz Financing<br>
Tech Stack: Java, Python, Nodejs, Flask, Springboot, Reactjs, Postgresql, Cursor, VectorDB, LLMs<br><br>
I’ve attached my resume for your reference and would be grateful if you could consider me for any suitable SDE openings.<br><br>
Regards,<br>
{sender_name}<br>
Mobile: +917355603902
"""
    elif template_type == "casual":
        html = f"""Hi {name},<br><br>
I'm <b>{sender_name}</b>, a software engineer with {sender_exp} of experience building high-performance systems. I'm currently looking for new opportunities as a <b>{role}</b> and I've been following the great work your team is doing at {company}.<br><br>
I'm confident I can make an immediate impact and would love to chat if you have any open roles matching my background.<br><br>
Best,<br>
<b>{sender_name}</b><br>
Email: {sender_email}
"""
    elif template_type == "short":
        html = f"""Hi {name},<br><br>
I'm reaching out to express my interest in joining {company} as a {role}. I have {sender_exp} of experience in backend development and system design.<br><br>
Would love to connect and share my resume if you're actively hiring!<br><br>
Best regards,<br>
<b>{sender_name}</b><br>
Email: {sender_email}
"""
    else: # formal
        html = f"""Hi {name},<br><br>
I’m <b>{sender_name}</b>, with strong experience in developing <b>high-performance and scalable systems</b>.<br><br>
<b>Experience:</b> {sender_exp}<br>
<b>Role:</b> {role}<br><br>
With a solid foundation in <b>system design</b>, <b>backend development</b>, and <b>product-focused problem solving</b>, I’m confident in my ability to deliver <b>impactful, business-aligned solutions</b> that contribute meaningfully to <b>{company}’s engineering goals</b>.<br><br>
I’d appreciate the opportunity to connect and explore any openings under your leadership.<br><br>
Best regards,<br>
<b>{sender_name}</b><br>
<b>Email:</b> {sender_email}
"""
    return html.replace('\n', '')
