class AIEngineError(Exception):
    """Base exception class for AI Engine errors."""
    pass

class ModelLoadError(AIEngineError):
    """Raised when ML models fail to load."""
    pass

class CodeParsingError(AIEngineError):
    """Raised when code parsing fails."""
    pass

class PatternAnalysisError(AIEngineError):
    """Raised when pattern analysis fails."""
    pass

class KnowledgeBaseError(AIEngineError):
    """Raised when knowledge base operations fail."""
    pass

class DependencyAnalysisError(AIEngineError):
    """Raised when dependency analysis fails."""
    pass