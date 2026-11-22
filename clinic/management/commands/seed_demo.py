from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from clinic.models import (
    BlogPost,
    DoctorProfile,
    FAQ,
    Service,
    SiteSettings,
    Testimonial,
)

SERVICES = [
    {
        "name": "General Assessment",
        "icon": "posture",
        "duration_minutes": 45,
        "price": 500,
        "is_featured": True,
        "order": 1,
        "short_description": "A thorough first visit to understand your pain, movement, and goals.",
        "description": (
            "Your first appointment is about listening as much as it is about assessing. "
            "We take a full history, examine how you move, and identify the root cause of your symptoms.\n\n"
            "You leave with a clear explanation of what is happening and a personalised plan for recovery."
        ),
    },
    {
        "name": "Manual Therapy",
        "icon": "massage",
        "duration_minutes": 45,
        "price": 600,
        "is_featured": True,
        "order": 2,
        "short_description": "Skilled hands-on techniques to release tension, restore motion, and ease pain.",
        "description": (
            "Manual therapy uses precise, hands-on techniques to mobilise joints, release tight soft tissue, "
            "and restore normal movement patterns.\n\n"
            "It is particularly effective for stiff joints, persistent pain, and restrictions that exercise alone "
            "cannot resolve. Every technique is adapted to your comfort and response."
        ),
    },
    {
        "name": "Sports Injury Rehabilitation",
        "icon": "sports",
        "duration_minutes": 60,
        "price": 700,
        "is_featured": True,
        "order": 3,
        "short_description": "Structured recovery that gets you back to training stronger than before.",
        "description": (
            "Whether you're a weekend runner or a competitive athlete, returning to sport safely takes more than "
            "resting an injury.\n\n"
            "We build a phased rehabilitation programme that restores strength, power, and confidence — with clear "
            "milestones so you know when it's safe to progress."
        ),
    },
    {
        "name": "Post-Surgical Rehabilitation",
        "icon": "rehab",
        "duration_minutes": 60,
        "price": 750,
        "is_featured": True,
        "order": 4,
        "short_description": "Guided recovery after surgery, protecting your repair and rebuilding strength.",
        "description": (
            "Recovery after surgery is a partnership between you, your surgeon, and your physiotherapist.\n\n"
            "We follow evidence-based protocols tailored to your procedure, protecting the repair while gradually "
            "restoring movement, strength, and function. We coordinate closely with your surgical team when needed."
        ),
    },
    {
        "name": "Chronic Pain Management",
        "icon": "pain",
        "duration_minutes": 45,
        "price": 650,
        "is_featured": True,
        "order": 5,
        "short_description": "A calm, evidence-based approach to persistent pain that has not settled.",
        "description": (
            "Persistent pain is complex, and it deserves more than a one-size-fits-all answer.\n\n"
            "We combine graded movement, manual therapy, education, and practical pacing strategies to help you "
            "regain function and confidence. The goal is not just less pain — it is a better life."
        ),
    },
    {
        "name": "Posture & Ergonomic Correction",
        "icon": "posture",
        "duration_minutes": 45,
        "price": 550,
        "is_featured": True,
        "order": 6,
        "short_description": "Practical solutions for desk-related neck, shoulder, and back discomfort.",
        "description": (
            "Long hours at a desk can leave you stiff, aching, and fatigued. The fix is rarely just 'sit up straight'.\n\n"
            "We assess your posture, workstation, and daily habits, then build a plan that combines targeted exercise "
            "with realistic ergonomic changes you can actually maintain."
        ),
    },
    {
        "name": "Dry Needling & Soft Tissue",
        "icon": "knee",
        "duration_minutes": 30,
        "price": 450,
        "is_featured": False,
        "order": 7,
        "short_description": "Targeted release for stubborn trigger points and muscular tightness.",
        "description": (
            "Dry needling targets trigger points and tight bands of muscle that refer pain and restrict movement.\n\n"
            "It is often combined with manual therapy and exercise for a more complete result. We explain every step "
            "and always work within your comfort."
        ),
    },
    {
        "name": "Neurological Rehabilitation",
        "icon": "neuro",
        "duration_minutes": 60,
        "price": 800,
        "is_featured": False,
        "order": 8,
        "short_description": "Specialist support for movement and balance after neurological conditions.",
        "description": (
            "Neurological rehabilitation focuses on helping you move, balance, and function as independently as possible.\n\n"
            "Programmes are tailored to your condition and goals, with careful progression and plenty of encouragement "
            "along the way."
        ),
    },
]

TESTIMONIALS = [
    ("Sarah M.", 5, "After years of lower back pain, I finally feel like myself again. Dr. Osama took the time to understand my goals and gave me a plan I could actually follow.", "chronic-pain-management"),
    ("Ahmed R.", 5, "I tore my hamstring playing football and was worried I'd never get back to full speed. The rehab programme was clear, progressive, and genuinely got me there.", "sports-injury-rehabilitation"),
    ("Layla K.", 5, "Post-surgery I was nervous about moving again. Dr. Osama was patient, reassuring, and incredibly knowledgeable. My recovery went better than I expected.", "post-surgical-rehabilitation"),
    ("Omar H.", 5, "The neck pain from desk work had become normal for me. A few weeks of treatment and simple changes made a huge difference. Highly recommended.", "posture-ergonomic-correction"),
    ("Nour A.", 5, "Professional, warm, and thorough. Every session was tailored and I never felt rushed. My shoulder mobility is better than it has been in years.", "manual-therapy"),
    ("Youssef S.", 5, "I appreciated how clearly everything was explained. I understood my injury for the first time and felt in control of my recovery.", "general-assessment"),
]

FAQS = [
    ("Do I need a referral to book?", "No referral is needed. You can book directly online, and we will assess your needs on your first visit."),
    ("What should I wear to my appointment?", "Comfortable, loose clothing that allows you to move freely and gives access to the area being treated. Shorts and a t-shirt are ideal for most assessments."),
    ("How long does a session take?", "Most sessions last between 30 and 60 minutes depending on the service. Your first assessment usually takes around 45 minutes."),
    ("How many sessions will I need?", "It depends on your condition and goals. After your assessment, Dr. Osama will give you a realistic estimate and review progress as you go."),
    ("Do you treat sports injuries?", "Yes. Sports injury rehabilitation is a core part of the practice, from acute sprains to return-to-sport programmes for competitive athletes."),
    ("Is physiotherapy painful?", "Treatment should never be unbearable. Some techniques may feel intense briefly, but we always work within your comfort and adjust as needed."),
    ("Can I book for a family member?", "Yes. Simply provide their details when booking, or call the clinic and we will help arrange the appointment."),
    ("What is your cancellation policy?", "Please give at least 24 hours' notice if you need to reschedule or cancel, so we can offer the slot to another patient."),
]

POSTS = [
    {
        "title": "5 Daily Habits That Protect Your Lower Back",
        "excerpt": "Small, consistent choices do more for your spine than any single exercise. Here are five habits worth building.",
        "tags": "Back health, Prevention, Daily movement",
        "days_ago": 6,
        "content": (
            "Lower back pain is rarely caused by one dramatic moment. More often, it builds quietly from days of "
            "sitting, lifting, and moving in ways your spine does not love.\n\n"
            "The good news is that small habits add up. Start with these five.\n\n"
            "1. Move every 30–45 minutes. Your spine loves variety more than any perfect posture. A two-minute walk "
            "or a gentle hinge reset can undo hours of stiffness.\n\n"
            "2. Learn to hinge, not bend. When you pick something up, push your hips back and keep your chest proud. "
            "Your hips are built for power; your lower back prefers to be a stable bridge.\n\n"
            "3. Build strength twice a week. A simple routine of hip hinges, squats, and carries makes your back more "
            "resilient. Strength is protection.\n\n"
            "4. Respect sleep. Recovery happens at night. A supportive mattress and a consistent sleep schedule are "
            "quietly powerful.\n\n"
            "5. Do not fear movement. Most back pain improves with gentle, graded activity. If something worries you, "
            "get it assessed rather than avoiding movement altogether."
        ),
    },
    {
        "title": "Returning to Sport After Injury: A Safe Timeline",
        "excerpt": "Getting back to training too soon is the most common cause of re-injury. Here is how to progress with confidence.",
        "tags": "Sports, Rehabilitation, Recovery",
        "days_ago": 20,
        "content": (
            "The urge to return to sport is understandable — but the body heals on its own timeline, not your "
            "calendar's.\n\n"
            "A safe return usually follows a progression: restore pain-free movement, rebuild strength, develop power, "
            "then practise the specific demands of your sport. Each stage should be passed without a flare-up before "
            "you move on.\n\n"
            "Pay attention to these green flags: no pain during daily activity, symmetrical strength, and confidence "
            "in the movements your sport requires. Red flags include swelling, sharp pain, or a feeling of instability.\n\n"
            "A physiotherapist can map your return with objective milestones, so you are not guessing. When in doubt, "
            "a slightly slower return is almost always the faster one."
        ),
    },
    {
        "title": "Why Posture Matters More Than You Think",
        "excerpt": "Posture is not about standing like a soldier. It is about giving your body options and reducing daily strain.",
        "tags": "Posture, Desk work, Neck pain",
        "days_ago": 34,
        "content": (
            "There is no single perfect posture. The real problem is staying in any one position for too long.\n\n"
            "Your body thrives on variety. Even a 'good' posture held for hours becomes a strain. The goal is to "
            "change positions regularly and build enough strength to make those positions easy.\n\n"
            "For desk workers, three changes tend to help most: set your screen at eye level, keep your feet supported, "
            "and take a short movement break every half hour. Add a simple daily routine for your upper back and hips.\n\n"
            "If neck or shoulder pain has become persistent, an assessment can identify whether mobility, strength, or "
            "your workstation is the main driver."
        ),
    },
    {
        "title": "Cold or Heat? What to Use for Pain",
        "excerpt": "A simple guide to choosing between ice and heat — and when neither is the answer.",
        "tags": "Pain relief, Recovery, Self-care",
        "days_ago": 52,
        "content": (
            "Ice and heat are both useful, but they do different jobs.\n\n"
            "Cold is best for a fresh injury or a flare-up: it narrows blood vessels, reduces swelling, and calms "
            "sharp pain. Use it for 10–15 minutes, always wrapped in a cloth.\n\n"
            "Heat is better for stiffness and muscle tightness. It increases blood flow and relaxes tissue, making it "
            "a good choice before gentle movement. Use it for 15–20 minutes.\n\n"
            "Neither replaces the most important treatment: appropriate movement and, when needed, professional "
            "assessment. If pain is severe, persistent, or comes with numbness or weakness, seek advice rather than "
            "relying on home remedies."
        ),
    },
]


class Command(BaseCommand):
    help = "Seed the clinic website with professional demo content."

    def handle(self, *args, **options):
        site = SiteSettings.load()
        site.clinic_name = "Sami Physiotherapy & Rehab. Center"
        site.doctor_name = "Dr. Osama Sami"
        site.tagline = "Movement restored. Life reclaimed."
        site.phone = "+91 98520 60649"
        site.whatsapp = "919852060649"
        site.email = "samiphysio1992@gmail.com"
        site.address = "Gaushala Rd, Doctors Colony, Siwan, Bihar 841227, India"
        site.location_short = "Siwan, Bihar"
        site.directions_url = "https://maps.app.goo.gl/9h8JbgSBrXt8K8qC7?g_st=aw"
        site.map_embed_url = (
            "https://www.google.com/maps?q=Gaushala+Rd,+Doctors+Colony,"
            "+Siwan,+Bihar+841227&z=16&output=embed"
        )
        site.working_hours = "Mon – Thu & Sat – Sun: 9:00 AM – 5:00 PM"
        site.facebook = ""
        site.instagram = "https://www.instagram.com/osamasami2511/"
        site.linkedin = ""
        site.youtube = ""
        site.hero_heading = "Expert Physiotherapy for a Stronger, Pain\u2011Free Life"
        site.hero_subheading = (
            "Personalised, evidence-based rehabilitation guided by over a decade of clinical "
            "experience — so you can move with confidence again."
        )
        site.about_short = (
            "For more than ten years, Dr. Osama Sami has helped patients recover from injury, "
            "manage chronic pain, and return to the activities they love."
        )
        site.years_experience = 10
        site.patients_treated = 4500
        site.success_rate = 98
        site.save()

        doctor = DoctorProfile.load()
        doctor.name = "Dr. Osama Sami"
        doctor.title = "Consultant Physiotherapist"
        doctor.years_experience = 10
        doctor.bio = (
            "Dr. Osama Sami is a consultant physiotherapist whose practice is built on a simple belief: every "
            "patient deserves a plan designed around their body, their goals, and their life. Over more than ten "
            "years, he has guided thousands of patients through injury, surgery, and chronic pain.\n\n"
            "His approach blends evidence-based manual therapy with progressive exercise, education, and genuine "
            "partnership — so recovery does not just happen in the clinic, it lasts."
        )
        doctor.credentials = (
            "Bachelor of Physiotherapy (BPT)\n"
            "Master of Physiotherapy (MPT)\n"
            "Consultant Physiotherapist"
        )
        doctor.specialties = (
            "Spine & posture rehabilitation\n"
            "Sports injury recovery\n"
            "Post-surgical rehabilitation\n"
            "Chronic pain management\n"
            "Manual therapy & dry needling"
        )
        doctor.save()

        for data in SERVICES:
            slug = data["name"].lower().replace(" & ", "-").replace(" ", "-")
            slug = slug.replace("--", "-")
            defaults = {**data, "price": None}
            Service.objects.update_or_create(slug=slug, defaults=defaults)

        if not Testimonial.objects.exists():
            for name, rating, quote, slug in TESTIMONIALS:
                service = Service.objects.filter(slug=slug).first()
                Testimonial.objects.create(
                    patient_name=name, rating=rating, quote=quote, service=service
                )

        if not FAQ.objects.exists():
            for order, (question, answer) in enumerate(FAQS, start=1):
                FAQ.objects.create(question=question, answer=answer, order=order)

        for post in POSTS:
            slug = post["title"].lower().replace(":", "").replace("?", "").replace(" ", "-")
            slug = slug.replace("--", "-")
            BlogPost.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": post["title"],
                    "excerpt": post["excerpt"],
                    "content": post["content"],
                    "tags": post["tags"],
                    "is_published": True,
                    "published_at": timezone.now() - timedelta(days=post["days_ago"]),
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo content seeded successfully."))
