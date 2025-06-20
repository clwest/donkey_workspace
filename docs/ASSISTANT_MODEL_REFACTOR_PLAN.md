# Assistant Model Refactoring Strategy

## Overview

The current Assistant model contains 92 fields, violating the Single Responsibility Principle and making it difficult to maintain. This document outlines a comprehensive refactoring strategy using composition and modular models.

## Current Problems

1. **God Object Anti-pattern**: 92 fields in a single model
2. **Mixed Concerns**: Identity, configuration, monitoring, and UI settings in one place
3. **Performance Issues**: Loading all fields even when only a subset is needed
4. **Maintenance Nightmare**: Hard to add new features without making the model even larger
5. **Testing Complexity**: Difficult to unit test specific behaviors

## Proposed Architecture

### Core Design Principles

1. **Composition over Inheritance**: Use OneToOne relationships for logical groupings
2. **Domain-Driven Design**: Each model represents a specific domain concept
3. **Lazy Loading**: Only load related models when needed
4. **Backward Compatibility**: Maintain existing API through properties and methods

## New Model Structure

### 1. Core Assistant Model (Slim)
```python
class Assistant(models.Model):
    """Core assistant entity with essential fields only"""
    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    slug = models.SlugField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Ownership & Status
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_demo = models.BooleanField(default=False)
    
    # Relationships
    parent_assistant = models.ForeignKey('self', null=True, blank=True)
    current_project = models.ForeignKey('project.AssistantProject', null=True)
    
    # Core References (OneToOne relationships created automatically)
    # - identity (AssistantIdentity)
    # - configuration (AssistantConfiguration)
    # - capabilities (AssistantCapabilities)
    # - growth (AssistantGrowth)
    # - quality (AssistantQuality)
    # - display (AssistantDisplay)
    
    class Meta:
        db_table = 'assistants_assistant'
        indexes = [
            models.Index(fields=['created_by', 'is_active']),
            models.Index(fields=['slug']),
        ]
```

### 2. Assistant Identity Model
```python
class AssistantIdentity(models.Model):
    """Personality and character traits"""
    assistant = models.OneToOneField(
        Assistant, 
        on_delete=models.CASCADE, 
        related_name='identity'
    )
    
    # Basic Identity
    description = models.TextField()
    specialty = models.CharField(max_length=255)
    avatar = models.CharField(max_length=512, null=True)
    
    # Personality
    personality = models.TextField()
    tone = models.CharField(max_length=255)
    traits = models.JSONField(default=dict)
    values = models.JSONField(default=list)
    motto = models.TextField(null=True)
    
    # Archetypes
    archetype = models.CharField(max_length=100, null=True)
    archetype_path = models.CharField(max_length=255, null=True)
    dream_symbol = models.CharField(max_length=100, null=True)
    
    # Persona
    persona_mode = models.CharField(max_length=50, default='balanced')
    persona_summary = models.TextField(null=True)
    personality_description = models.TextField(null=True)
    
    # Emotional State
    mood_stability_index = models.FloatField(default=0.7)
    last_mood_shift = models.DateTimeField(null=True)
    created_from_mood = models.CharField(max_length=50, null=True)
    
    # Introduction
    intro_text = models.TextField(null=True)
    init_reflection = models.TextField(null=True)
    
    class Meta:
        db_table = 'assistants_identity'
```

### 3. Assistant Configuration Model
```python
class AssistantConfiguration(models.Model):
    """Technical and behavioral configuration"""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='configuration'
    )
    
    # AI Model Settings
    preferred_model = models.CharField(max_length=100, default='gpt-4')
    thinking_style = models.CharField(max_length=50, default='analytical')
    memory_mode = models.CharField(max_length=50, default='standard')
    
    # System Prompt
    system_prompt = models.ForeignKey('prompts.Prompt', null=True)
    prompt_title = models.CharField(max_length=255, null=True)
    prompt_notes = models.TextField(null=True)
    boost_prompt_in_system = models.BooleanField(default=False)
    
    # Collaboration Settings
    delegation_threshold_tokens = models.IntegerField(default=1000)
    auto_delegate_on_feedback = models.BooleanField(default=False)
    collaboration_style = models.CharField(max_length=50, default='cooperative')
    preferred_conflict_resolution = models.CharField(max_length=50, default='consensus')
    
    # Feature Flags
    live_relay_enabled = models.BooleanField(default=False)
    memory_summon_enabled = models.BooleanField(default=True)
    auto_reflect_on_message = models.BooleanField(default=True)
    
    # RAG Configuration
    preferred_rag_vector = models.CharField(max_length=50, default='contextual')
    min_score_threshold = models.FloatField(default=0.7)
    require_trusted_anchors = models.BooleanField(default=False)
    suppress_unstable_anchors = models.BooleanField(default=True)
    anchor_weight_profile = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'assistants_configuration'
```

### 4. Assistant Capabilities Model
```python
class AssistantCapabilities(models.Model):
    """Skills, capabilities, and competencies"""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='capabilities'
    )
    
    # Core Capabilities
    capabilities = models.JSONField(default=dict)
    capability_embedding = ArrayField(
        models.FloatField(),
        size=768,
        null=True
    )
    
    # Skills & Badges
    skill_badges = models.JSONField(default=list)
    primary_badge = models.CharField(max_length=100, null=True)
    badge_history = models.JSONField(default=list)
    
    # Knowledge Integration
    glossary_score = models.FloatField(default=0.0)
    embedding_index = models.IntegerField(null=True)
    embedding = ArrayField(models.FloatField(), size=768, null=True)
    initial_embedding = ArrayField(models.FloatField(), size=768, null=True)
    
    # Ideology & Beliefs
    belief_vector = ArrayField(models.FloatField(), size=768, null=True)
    ideology = models.CharField(max_length=100, null=True)
    is_alignment_flexible = models.BooleanField(default=True)
    
    # Empathy Profile
    avg_empathy_score = models.FloatField(default=0.5)
    empathy_tags = models.JSONField(default=list)
    preferred_scene_tags = models.JSONField(default=list)
    
    class Meta:
        db_table = 'assistants_capabilities'
```

### 5. Assistant Growth Model
```python
class AssistantGrowth(models.Model):
    """Growth, nurturing, and evolution tracking"""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='growth'
    )
    
    # Growth Tracking
    growth_stage = models.CharField(max_length=50, default='seed')
    growth_points = models.IntegerField(default=0)
    nurture_started_at = models.DateTimeField(null=True)
    growth_unlocked_at = models.DateTimeField(null=True)
    
    # Memory & Learning
    growth_summary_memory = models.ForeignKey(
        'memory.MemoryEntry',
        null=True,
        on_delete=models.SET_NULL
    )
    memory_context = models.ForeignKey(
        'memory.MemoryContext',
        null=True,
        on_delete=models.SET_NULL
    )
    default_memory_chain = models.ForeignKey(
        'assistants.AssistantMemoryChain',
        null=True,
        on_delete=models.SET_NULL
    )
    
    # Spawning & Inheritance
    spawned_by = models.ForeignKey(
        Assistant,
        null=True,
        related_name='spawned_growth',
        on_delete=models.SET_NULL
    )
    spawn_reason = models.TextField(null=True)
    spawned_traits = models.JSONField(default=dict)
    inherited_tone = models.CharField(max_length=255, null=True)
    
    # Mentorship
    mentor_assistant = models.ForeignKey(
        Assistant,
        null=True,
        related_name='mentored_growth',
        on_delete=models.SET_NULL
    )
    mentor_for_demo_clone = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'assistants_growth'
```

### 6. Assistant Quality Model
```python
class AssistantQuality(models.Model):
    """Quality metrics, monitoring, and trust scores"""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='quality'
    )
    
    # Trust Metrics
    last_trust_score = models.FloatField(default=0.5)
    last_trust_components = models.JSONField(default=dict)
    
    # Quality Certification
    certified_rag_ready = models.BooleanField(default=False)
    rag_certification_date = models.DateField(null=True)
    rag_certification_notes = models.TextField(null=True)
    last_rag_certified_at = models.DateTimeField(null=True)
    
    # Health Monitoring
    last_drift_check = models.DateTimeField(null=True)
    needs_recovery = models.BooleanField(default=False)
    
    # Reflection Tracking
    last_reflection_attempted_at = models.DateTimeField(null=True)
    last_reflection_successful = models.BooleanField(default=True)
    reflection_error = models.TextField(null=True)
    birth_reflection_retry_count = models.IntegerField(default=0)
    can_retry_birth_reflection = models.BooleanField(default=True)
    
    # Performance Metrics
    avg_response_time = models.FloatField(default=0.0)
    total_interactions = models.IntegerField(default=0)
    success_rate = models.FloatField(default=1.0)
    
    class Meta:
        db_table = 'assistants_quality'
        indexes = [
            models.Index(fields=['last_trust_score']),
            models.Index(fields=['certified_rag_ready']),
        ]
```

### 7. Assistant Display Model
```python
class AssistantDisplay(models.Model):
    """UI/UX settings and display preferences"""
    assistant = models.OneToOneField(
        Assistant,
        on_delete=models.CASCADE,
        related_name='display'
    )
    
    # Feature Flags
    is_featured = models.BooleanField(default=False)
    featured_rank = models.IntegerField(null=True)
    is_guide = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    
    # Display Settings
    show_intro_splash = models.BooleanField(default=True)
    show_trail_recap = models.BooleanField(default=True)
    auto_start_chat = models.BooleanField(default=False)
    avatar_style = models.CharField(max_length=50, default='default')
    
    # Demo Settings
    demo_slug = models.SlugField(max_length=255, null=True, unique=True)
    is_demo_clone = models.BooleanField(default=False)
    boosted_from_demo = models.BooleanField(default=False)
    
    # Lifecycle
    is_ephemeral = models.BooleanField(default=False)
    expiration_event = models.ForeignKey(
        'agents.SwarmMemoryEntry',
        null=True,
        on_delete=models.SET_NULL
    )
    
    class Meta:
        db_table = 'assistants_display'
        indexes = [
            models.Index(fields=['is_featured', 'featured_rank']),
        ]
```

## Migration Strategy

### Phase 1: Create New Models (Week 1)
1. Create all new model definitions
2. Generate migrations without running them
3. Add backward compatibility properties to Assistant model
4. Create comprehensive test suite

### Phase 2: Data Migration (Week 2)
```python
def migrate_assistant_data(apps, schema_editor):
    Assistant = apps.get_model('assistants', 'Assistant')
    AssistantIdentity = apps.get_model('assistants', 'AssistantIdentity')
    # ... other models
    
    for assistant in Assistant.objects.all():
        # Create Identity
        AssistantIdentity.objects.create(
            assistant=assistant,
            description=assistant.description,
            personality=assistant.personality,
            # ... map all fields
        )
        
        # Create Configuration
        AssistantConfiguration.objects.create(
            assistant=assistant,
            preferred_model=assistant.preferred_model,
            # ... map all fields
        )
        
        # ... create other related models
```

### Phase 3: Update Code (Week 3-4)
1. Update all serializers to use new model structure
2. Modify views to use select_related for performance
3. Update all queries to use new relationships
4. Add deprecation warnings for old field access

### Phase 4: Cleanup (Week 5)
1. Remove old fields from Assistant model
2. Drop old columns from database
3. Update all tests
4. Update documentation

## Backward Compatibility

### Property-based Access
```python
class Assistant(models.Model):
    # ... core fields ...
    
    @property
    def personality(self):
        """Backward compatibility for personality field"""
        return self.identity.personality if hasattr(self, 'identity') else None
    
    @personality.setter
    def personality(self, value):
        if hasattr(self, 'identity'):
            self.identity.personality = value
            self.identity.save()
    
    @property
    def preferred_model(self):
        """Backward compatibility for preferred_model field"""
        return self.configuration.preferred_model if hasattr(self, 'configuration') else 'gpt-4'
    
    # ... add properties for all migrated fields ...
```

### Manager Methods for Common Queries
```python
class AssistantManager(models.Manager):
    def get_queryset(self):
        """Always prefetch related models for common access patterns"""
        return super().get_queryset().select_related(
            'identity', 'configuration', 'capabilities'
        )
    
    def active(self):
        """Get all active assistants"""
        return self.get_queryset().filter(is_active=True)
    
    def with_full_profile(self):
        """Load all related models for detailed views"""
        return self.get_queryset().select_related(
            'identity', 'configuration', 'capabilities',
            'growth', 'quality', 'display'
        ).prefetch_related(
            'documents', 'sub_assistants'
        )
```

## Performance Benefits

1. **Selective Loading**: Load only needed components
2. **Optimized Queries**: Use select_related for known access patterns
3. **Smaller Cache Footprint**: Cache individual components
4. **Parallel Processing**: Update different aspects concurrently

## Example Usage

### Creating an Assistant
```python
# Old way
assistant = Assistant.objects.create(
    name="Helper",
    personality="Friendly and helpful",
    preferred_model="gpt-4",
    # ... 90+ more fields
)

# New way
assistant = Assistant.objects.create(
    name="Helper",
    created_by=user
)
AssistantIdentity.objects.create(
    assistant=assistant,
    personality="Friendly and helpful"
)
AssistantConfiguration.objects.create(
    assistant=assistant,
    preferred_model="gpt-4"
)
```

### Querying Assistants
```python
# Get assistant with identity only
assistant = Assistant.objects.select_related('identity').get(pk=id)

# Get full profile for detailed view
assistant = Assistant.objects.with_full_profile().get(pk=id)

# Get assistants for list view (minimal fields)
assistants = Assistant.objects.active().only(
    'id', 'name', 'slug'
).select_related('identity__avatar', 'identity__specialty')
```

## Testing Strategy

1. **Unit Tests**: Test each model independently
2. **Integration Tests**: Test model interactions
3. **Performance Tests**: Ensure queries are optimized
4. **Migration Tests**: Verify data integrity during migration

## Monitoring & Rollback Plan

1. **Feature Flags**: Use flags to switch between old/new implementations
2. **Metrics**: Monitor query performance and error rates
3. **Rollback**: Keep old columns for 30 days after migration
4. **Gradual Rollout**: Migrate by user cohorts

## Success Criteria

- [ ] All existing functionality preserved
- [ ] API response times improved by 30%
- [ ] Database query count reduced by 50%
- [ ] Zero data loss during migration
- [ ] Test coverage maintained at 80%+

## Next Steps

1. Review and approve this design
2. Create proof-of-concept branch
3. Implement Phase 1 models
4. Run performance benchmarks
5. Plan migration timeline