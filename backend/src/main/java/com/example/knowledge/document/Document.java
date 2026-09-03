package com.example.knowledge.document;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "documents")
public class Document {

    @Id
    private String id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String source;

    @Column(nullable = false)
    private String scope;

    @Column(name = "owner_id", nullable = false)
    private String ownerId;

    @Column(name = "chunk_count", nullable = false)
    private int chunkCount;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    protected Document() {}

    public Document(String title, String source, String scope, String ownerId) {
        this.id = UUID.randomUUID().toString();
        this.title = title;
        this.source = source;
        this.scope = scope;
        this.ownerId = ownerId;
        this.createdAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getSource() {
        return source;
    }

    public String getScope() {
        return scope;
    }

    public String getOwnerId() {
        return ownerId;
    }

    public int getChunkCount() {
        return chunkCount;
    }

    public void setChunkCount(int chunkCount) {
        this.chunkCount = chunkCount;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
