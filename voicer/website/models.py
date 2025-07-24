from django.db import models
from django.contrib.auth.models import User

# =====================
# User Profile
# =====================
class UserProfile(models.Model):
    USER_ROLES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    audio_file = models.FileField(upload_to='audio/')
    rate =models.BigIntegerField(default=123)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    # 🔗 One-to-One: User ↔ UserProfile
    # Each user has exactly one profile that determines if they are a seller or buyer.
    # 📌 Example:
    # User: 'alex' → UserProfile: role='seller', bio='British voice actor with 10 years of experience'


# =====================
# Voiceover Services
# =====================
class VoiceoverService(models.Model):
    seller = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    audio_sample = models.FileField(upload_to='samples/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.seller.user.username}"

    # 🔗 ForeignKey: VoiceoverService → UserProfile (seller)
    # A seller can list multiple services, each associated with their profile.
    # 📌 Example:
    # Seller: 'alex' → Services: ['Warm British Voiceover', 'Commercial Promo Voice']


# =====================
# Orders
# =====================
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    service = models.ForeignKey(VoiceoverService, on_delete=models.CASCADE)
    buyer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requirements = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.service.title} for {self.buyer.user.username}"

    # 🔗 ForeignKey: Order → VoiceoverService
    # Each order is placed for a specific service.
    # 📌 Example:
    # Order: #1001 → Service: "Warm British Voiceover"

    # 🔗 ForeignKey: Order → UserProfile (buyer)
    # Each order is placed by a buyer.
    # 📌 Example:
    # Buyer: 'sara' places Order #1001 for 'alex's voiceover service.


# =====================
# Chat Messages
# =====================
class ChatMessage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.user.username} at {self.timestamp}"

    # 🔗 ForeignKey: ChatMessage → Order
    # Each message belongs to a specific order conversation thread.
    # 📌 Example:
    # Order #1001 → Message: "Please add background music"

    # 🔗 ForeignKey: ChatMessage → UserProfile (sender)
    # Message sender can be the buyer or seller in the context of the order.
    # 📌 Example:
    # Sender: 'alex' (seller) replies to 'sara' (buyer).


# =====================
# Reviews
# =====================
class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.user.username} for Order #{self.order.id}"

    # 🔗 OneToOneField: Review → Order
    # Each order can have only one review associated with it.
    # 📌 Example:
    # Order #1001 → Review: 5 stars, "Excellent delivery"

    # 🔗 ForeignKey: Review → UserProfile (reviewer)
    # The person writing the review (typically the buyer).
    # 📌 Example:
    # Buyer 'sara' gives feedback on 'alex’s' voiceover service.


# =====================
# Direct User-to-User Chat
# =====================
class DirectChatMessage(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_direct_messages')
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_direct_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Direct message from {self.sender.user.username} to {self.recipient.user.username} at {self.timestamp}"
