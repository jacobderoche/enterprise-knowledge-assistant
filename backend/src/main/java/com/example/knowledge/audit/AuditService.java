package com.example.knowledge.audit;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuditService {

    private final AuditLogRepository repository;

    public AuditService(AuditLogRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public void record(String userId, String action, String resourceId, String detail) {
        repository.save(new AuditLog(userId, action, resourceId, detail));
    }
}
