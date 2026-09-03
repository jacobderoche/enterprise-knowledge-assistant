package com.example.knowledge.audit;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** Admin-only view of the audit trail (secured by /api/admin/** rule + ADMIN role). */
@RestController
@RequestMapping("/api/admin/audit")
public class AuditController {

    private final AuditLogRepository repository;

    public AuditController(AuditLogRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public List<AuditLog> all() {
        return repository.findAll();
    }
}
