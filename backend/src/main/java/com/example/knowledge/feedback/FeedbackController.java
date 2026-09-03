package com.example.knowledge.feedback;

import com.example.knowledge.audit.AuditService;
import com.example.knowledge.feedback.dto.FeedbackRequest;
import com.example.knowledge.security.AuthenticatedUser;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/feedback")
public class FeedbackController {

    private final FeedbackRepository repository;
    private final AuditService audit;

    public FeedbackController(FeedbackRepository repository, AuditService audit) {
        this.repository = repository;
        this.audit = audit;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Feedback submit(@Valid @RequestBody FeedbackRequest request, Authentication authentication) {
        AuthenticatedUser user = AuthenticatedUser.from(authentication);
        Feedback feedback = repository.save(
                new Feedback(request.messageId(), user.userId(), request.rating(), request.comment()));
        audit.record(user.userId(), "FEEDBACK", request.messageId(), "rating=" + request.rating());
        return feedback;
    }
}
