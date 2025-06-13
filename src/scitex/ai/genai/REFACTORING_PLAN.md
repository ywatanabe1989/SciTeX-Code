# GenAI Module Refactoring Plan - Phase 2

## Status Update (2024-11-15)

### Phase 2.1 ✅ COMPLETED
All 9 components have been successfully extracted from the BaseGenAI god object:

1. **auth_manager.py** (134 lines) - API key management and validation
2. **model_registry.py** (188 lines) - Model information and capabilities registry
3. **chat_history.py** (202 lines) - Conversation history with role enforcement
4. **cost_tracker.py** (197 lines) - Token usage and cost tracking
5. **response_handler.py** (242 lines) - Response processing for static/streaming
6. **image_processor.py** (248 lines) - Image processing for multimodal inputs
7. **base_provider.py** (240 lines) - Abstract base class defining provider interface
8. **provider_base.py** (300 lines) - Composition-based implementation combining all components
9. **provider_factory.py** (129 lines) - Factory pattern for provider instantiation

**Total**: 1,880 lines of well-organized, single-responsibility components replacing the 344-line god object.

### Next Priority: Testing
The components are created but need comprehensive test implementation to match the new architecture.

## Current Analysis

### BaseGenAI God Object (344 lines)
The BaseGenAI class currently handles multiple responsibilities:

1. **Authentication & API Key Management** (lines 44, 304-308)
   - API key validation
   - Masked API key generation
   
2. **Model Registry & Verification** (lines 58-59, 65-83, 203-212, 297-303)
   - Model availability checking
   - Provider-model mapping
   - Model verification

3. **Chat History Management** (lines 55, 214-239, 275-295)
   - History storage
   - Role alternation enforcement
   - User-first enforcement
   - Base64 image encoding

4. **Cost Tracking** (lines 50-51, 313-314)
   - Input/output token counting
   - Cost calculation

5. **Response Processing** (lines 104-163, 164-183)
   - Static vs stream response handling
   - Output formatting
   - Error message handling

6. **Image Processing** (lines 240-274)
   - Image resizing
   - Base64 encoding
   - Multiple format support

7. **Client Initialization** (line 59, abstract method)
   - Provider-specific client setup

8. **API Communication** (abstract methods)
   - Static API calls
   - Stream API calls
   - History formatting

9. **Error Handling** (lines 52, 85-102)
   - Error message accumulation
   - Error streaming

## Proposed Component Architecture

### 1. Core Components

#### `auth_manager.py`
```python
class AuthManager:
    """Handles API key management and validation"""
    def __init__(self, api_key: str, provider: str)
    def validate_key(self) -> bool
    def get_masked_key(self) -> str
    def get_key_from_env(provider: str) -> Optional[str]
```

#### `model_registry.py`
```python
class ModelRegistry:
    """Central registry for model information"""
    def get_models_for_provider(provider: str) -> List[str]
    def verify_model(provider: str, model: str) -> bool
    def get_model_info(model: str) -> ModelInfo
    def list_all_models() -> Dict[str, List[str]]
```

#### `chat_history.py`
```python
class ChatHistory:
    """Manages conversation history"""
    def __init__(self, n_keep: int = 1)
    def add_message(role: str, content: str, images: Optional[List])
    def get_history() -> List[Dict]
    def ensure_alternating() -> None
    def ensure_user_first() -> None
    def reset(system_message: Optional[str] = None)
```

#### `cost_tracker.py`
```python
class CostTracker:
    """Tracks token usage and costs"""
    def __init__(self, model: str)
    def add_tokens(input_tokens: int, output_tokens: int)
    def get_cost() -> float
    def get_usage() -> Dict[str, int]
```

#### `response_handler.py`
```python
class ResponseHandler:
    """Handles response processing and formatting"""
    def process_static(response: Any) -> str
    def process_stream(stream: Generator) -> Generator[str, None, None]
    def format_output(text: str) -> str
```

#### `image_processor.py`
```python
class ImageProcessor:
    """Handles image processing for multimodal inputs"""
    def process_image(image: Union[str, bytes], max_size: int = 512) -> str
    def resize_image(image: Image, max_size: int) -> Image
    def to_base64(image: Image) -> str
```

### 2. Base Classes

#### `base_provider.py`
```python
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    def init_client(self) -> Any:
        """Initialize provider-specific client"""
        
    @abstractmethod
    def format_history(self, history: List[Dict]) -> List[Dict]:
        """Format history for provider API"""
        
    @abstractmethod
    def call_static(self, messages: List[Dict], **kwargs) -> Any:
        """Make static API call"""
        
    @abstractmethod
    def call_stream(self, messages: List[Dict], **kwargs) -> Generator:
        """Make streaming API call"""
```

#### `provider_base.py`
```python
class ProviderBase(BaseProvider):
    """Common implementation for providers using composition"""
    
    def __init__(self, config: ProviderConfig):
        self.auth = AuthManager(config.api_key, config.provider)
        self.models = ModelRegistry()
        self.history = ChatHistory(config.n_keep)
        self.costs = CostTracker(config.model)
        self.response_handler = ResponseHandler()
        self.image_processor = ImageProcessor()
        
        # Verify model before proceeding
        if not self.models.verify_model(config.provider, config.model):
            raise ValueError(f"Model {config.model} not available")
            
        self.client = self.init_client()
```

### 3. Provider Implementations

Each provider (Anthropic, OpenAI, etc.) will:
1. Inherit from `ProviderBase`
2. Implement only the abstract methods
3. Use composition to access shared functionality

Example:
```python
class AnthropicProvider(ProviderBase):
    def init_client(self) -> anthropic.Anthropic:
        return anthropic.Anthropic(api_key=self.auth.api_key)
        
    def format_history(self, history: List[Dict]) -> List[Dict]:
        # Anthropic-specific formatting
        ...
        
    def call_static(self, messages: List[Dict], **kwargs) -> Any:
        # Anthropic API call
        ...
```

### 4. Factory Pattern

#### `provider_factory.py`
```python
from enum import Enum
from typing import Type

class Provider(Enum):
    OPENAI = "OpenAI"
    ANTHROPIC = "Anthropic"
    GOOGLE = "Google"
    # ... etc

class ProviderFactory:
    _registry: Dict[Provider, Type[ProviderBase]] = {}
    
    @classmethod
    def register(cls, provider: Provider, implementation: Type[ProviderBase]):
        cls._registry[provider] = implementation
        
    @classmethod
    def create(cls, provider: Provider, config: ProviderConfig) -> ProviderBase:
        if provider not in cls._registry:
            raise ValueError(f"Provider {provider} not registered")
        return cls._registry[provider](config)
```

## Migration Strategy

### Phase 2.1: Extract Components ✅ COMPLETED
1. ✅ Create all component files with interfaces
2. ✅ Extract functionality from BaseGenAI
3. ⏳ Write unit tests for each component (next priority)

### Phase 2.2: Implement Provider Base (Day 5)
1. Create abstract base class
2. Implement composition-based base
3. Update one provider as proof of concept

### Phase 2.3: Migrate All Providers (Day 6)
1. Update all provider implementations
2. Implement type-safe factory
3. Ensure backward compatibility

## Benefits

1. **Single Responsibility**: Each component has one clear purpose
2. **Testability**: Components can be tested in isolation
3. **Reusability**: Components can be used independently
4. **Maintainability**: Changes isolated to specific components
5. **Type Safety**: Strong typing with enums and type hints
6. **Extensibility**: Easy to add new providers or features

## Backward Compatibility

The existing `genai_factory` function will continue to work:
```python
def genai_factory(model: str, **kwargs) -> BaseGenAI:
    # Map model to provider
    provider = get_provider_for_model(model)
    
    # Create config
    config = ProviderConfig(model=model, provider=provider, **kwargs)
    
    # Use new factory
    provider_impl = ProviderFactory.create(provider, config)
    
    # Wrap in backward-compatible interface if needed
    return LegacyWrapper(provider_impl)
```

## Next Steps

1. Get approval for this plan
2. Create component files
3. Write tests first (TDD)
4. Implement components
5. Migrate providers
6. Update documentation