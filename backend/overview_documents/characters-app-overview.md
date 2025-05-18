# Characters App

## Models

### CharacterProfile

    - name
    - slug
    - description
    - personality_traits
    - backstory
    - is_public
    - is_featured
    - created_by `fk User`
    - created_at
    - project `fk project.Project`
    - character_styles `M2M images.PromptHelper`

### CharacterStyle

    - character `FK CharacterProfile`
    - style_name
    - prompt_helper `FK images.PromptHelper`
    - prompt
    - negative_prompt
    - image_reference
    - created_at

### CharacterReferenceImage

    - character `fk CharacterProfile`
    - image
    - caption
    - alt_text
    - created_at
    - tags `M2M images.Tag (image tags need to move to mcp_core.Tags)`
    - style `fk images.PromptHelper`
    - is_primary

### CharacterTag

    - name
    - characters `m2m CharacterProfile`

### CharacterTrainingProfile

    - character `OneToOne CharacterProfile`
    - embedding
    - status
    - task_id
    - created_at
    - updated_at

## serializers.py

    - CharacterTagSerializer
    - TagImageSerializer
    - CharacterReferenceImageSerializer
    - PromptHelperSerializer
    - CharacterStyleSerializer
    - CharacterProfileSerializer
    - CharacterTrainingProfileSerializer

## tasks.py

    - train_character_embedding()

## views.py

    - CharacterProfileViewSet
    - CharacterStyleViewSet
    - CharacterReferenceImageViewSet
    - CharactersByProjectView
    - CharacterImagesView
    - NameGenerationView
    - CharacterSimilarityView
    - CharacterTrainingStatusView
    - CharacterProfileSimilarityView
    - CharacterTrainView
    - CharactersByProjectView
