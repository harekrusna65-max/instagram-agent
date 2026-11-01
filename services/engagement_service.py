"""
Engagement Service: Auto-DM responder and Comment Trigger Bot
"""

from typing import List, Dict, Any
from core.client import InstagramAgentClient
from services.ai_generator import AIGenerator
from database.db import (
    get_active_rules,
    is_interaction_processed,
    record_processed_interaction
)

class EngagementService:
    def __init__(self, client: InstagramAgentClient, ai: AIGenerator):
        self.client = client
        self.ai = ai

    def process_recent_post_comments(self, post_limit: int = 5) -> int:
        """
        Scan comments on recent posts. If comment contains trigger keywords,
        auto-reply to comment and/or send DM with link/details.
        """
        rules = get_active_rules()
        if not rules:
            return 0

        medias = self.client.get_user_medias(amount=post_limit)
        handled_count = 0

        for media in medias:
            try:
                comments = self.client.get_media_comments(media.id, amount=20)
                for comment in comments:
                    comment_id = str(comment.pk)
                    # Don't reply to our own comments
                    if str(comment.user.pk) == str(self.client.user_id):
                        continue

                    # Check if already handled
                    if is_interaction_processed(comment_id):
                        continue

                    comment_text_lower = comment.text.lower()
                    username = comment.user.username
                    user_pk = comment.user.pk

                    # Check against active keyword rules
                    for rule in rules:
                        kw = rule["keyword"].lower()
                        if kw in comment_text_lower:
                            print(f"[+] Keyword match '{kw}' by @{username} on post {media.code}")
                            
                            # 1. Like the comment
                            try:
                                self.client.client.comment_like(comment.pk)
                                print(f"    [✓] Liked comment #{comment_id}")
                            except Exception:
                                pass

                            # 2. Reply to comment if configured
                            if rule["reply_comment"]:
                                reply_text = rule["reply_comment"].replace("@user", f"@{username}")
                                try:
                                    self.client.reply_to_comment(media.id, reply_text, replied_to_comment_id=comment_id)
                                    print(f"    [✓] Replied to comment: {reply_text}")
                                except Exception as e:
                                    print(f"    [!] Failed to reply to comment: {e}")

                            # 3. Send DM if configured
                            if rule["reply_dm"]:
                                dm_text = rule["reply_dm"].replace("{name}", comment.user.full_name or username)
                                try:
                                    self.client.send_direct_message(dm_text, user_ids=[user_pk])
                                    print(f"    [✓] Sent DM to @{username}: {dm_text}")
                                except Exception as e:
                                    print(f"    [!] Failed to send DM: {e}")

                            record_processed_interaction(
                                interaction_type="comment",
                                external_id=comment_id,
                                user_id=str(user_pk),
                                username=username,
                                message_text=comment.text,
                                action_taken=f"rule:{kw}"
                            )
                            handled_count += 1
                            break

            except Exception as e:
                print(f"[!] Error reading comments for media {media.id}: {e}")

        return handled_count

    def process_unread_dms(self) -> int:
        """
        Check incoming DMs. If new unread message from a user, send an intelligent AI reply.
        """
        threads = self.client.get_direct_threads(amount=10)
        replied_count = 0

        for thread in threads:
            try:
                # Find messages not from us
                messages = thread.messages
                if not messages:
                    continue

                last_msg = messages[0]
                msg_id = str(last_msg.id)

                # Skip if from us
                if str(last_msg.user_id) == str(self.client.user_id):
                    continue

                # Skip if already handled
                if is_interaction_processed(msg_id):
                    continue

                msg_text = getattr(last_msg, "text", "")
                if not msg_text:
                    continue

                # Find sender user info
                sender_name = "there"
                user_pk = last_msg.user_id
                if thread.users:
                    for u in thread.users:
                        if u.pk == user_pk:
                            sender_name = u.full_name or u.username
                            break

                print(f"[+] New DM from {sender_name}: '{msg_text}'")
                reply = self.ai.generate_dm_reply(msg_text, sender_name)
                
                # Send reply to thread
                self.client.send_direct_message(reply, thread_id=thread.id)
                print(f"    [✓] AI DM Reply sent: {reply}")

                record_processed_interaction(
                    interaction_type="dm",
                    external_id=msg_id,
                    user_id=str(user_pk),
                    username=sender_name,
                    message_text=msg_text,
                    action_taken="ai_reply"
                )
                replied_count += 1

            except Exception as e:
                print(f"[!] Error processing thread {thread.id}: {e}")

        return replied_count
