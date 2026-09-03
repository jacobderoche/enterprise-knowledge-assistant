package com.example.knowledge.chat;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "messages")
public class Message {

    public enum Role { USER, ASSISTANT }

    @Id
    private String id;

    @Column(name = "conversation_id", nullable = false)
    private String conversationId;

    @Column(nullable = false)
    private String role;

    @Lob
    @Column(nullable = false)
    private String content;

    /** JSON blob of citations for assistant messages. */
    @Lob
    @Column(name = "citations_json")
    private String citationsJson;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    protected Message() {}

    public Message(String conversationId, Role role, String content, String citationsJson) {
        this.id = UUID.randomUUID().toString();
        this.conversationId = conversationId;
        this.role = role.name();
        this.content = content;
        this.citationsJson = citationsJson;
        this.createdAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getConversationId() {
        return conversationId;
    }

    public String getRole() {
        return role;
    }

    public String getContent() {
        return content;
    }

    public String getCitationsJson() {
        return citationsJson;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
