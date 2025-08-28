# YouTube Video Summarizer - Architecture Diagrams

This folder contains PlantUML diagrams that illustrate the architecture and design of the YouTube Video Summarizer application.

## Diagram Files

### 1. Architecture Diagram (`architecture.puml`)

**Purpose**: Shows the overall system architecture and component relationships.

**Contents**:

- External services (YouTube API, OpenAI API)
- CLI interface layer with Click framework
- Core application components
- Data processing pipeline
- Output layer with multiple formats
- Local storage components

**Key Features Illustrated**:

- Component separation and modularity
- External API integrations
- Data flow between layers
- Storage and caching mechanisms

### 2. Data Flow Diagram (`data_flow.puml`)

**Purpose**: Illustrates the complete data processing pipeline from user input to final output.

**Contents**:

- User input validation
- Video ID extraction process
- Transcript fetching workflow
- Text cleaning and processing
- AI summarization pipeline
- Output formatting options
- Error handling paths

**Key Features Illustrated**:

- Decision points and branching logic
- Different command types (extract, summarize, batch, info)
- Output format handling
- Error conditions and recovery

### 3. Component Interaction Diagram (`component_diagram.puml`)

**Purpose**: Details the internal component interactions and interfaces.

**Contents**:

- Interface definitions
- Component internal structure
- Inter-component communication
- External system connections
- Data flow annotations

**Key Features Illustrated**:

- Component responsibilities
- Interface contracts
- Dependency relationships
- Internal component structure

## Viewing the Diagrams

### Option 1: Online PlantUML Server

1. Copy the content of any `.puml` file
2. Go to [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
3. Paste the content and view the rendered diagram

### Option 2: Local PlantUML Installation

```bash
# Install PlantUML (requires Java)
# Download from: https://plantuml.com/download

# Generate PNG images
java -jar plantuml.jar diagrams/*.puml

# Generate SVG images
java -jar plantuml.jar -tsvg diagrams/*.puml
```

### Option 3: VS Code Extension

1. Install the "PlantUML" extension in VS Code
2. Open any `.puml` file
3. Use `Alt+D` to preview the diagram

## Diagram Conventions

### Colors and Styling

- **Blue**: CLI and user interface components
- **Green**: Core processing logic
- **Orange**: Data processing and transformation
- **Purple**: Output and storage operations
- **Red**: Error conditions and handling

### Component Types

- **Rectangles**: Application components
- **Clouds**: External services
- **Cylinders**: Data storage
- **Actors**: Users or external systems
- **Interfaces**: Component contracts

### Arrows and Connections

- **Solid arrows**: Direct dependencies or data flow
- **Dashed arrows**: Indirect relationships or "uses" relationships
- **Thick arrows**: Primary data flow paths
- **Colored arrows**: Different types of interactions

## Updating Diagrams

When modifying the application architecture:

1. **Update the relevant `.puml` files** to reflect changes
2. **Regenerate images** using one of the methods above
3. **Update documentation** if component responsibilities change
4. **Validate diagrams** ensure they accurately represent the code

### Best Practices for Diagram Updates

- Keep diagrams synchronized with code changes
- Use consistent naming between diagrams and code
- Add notes for complex interactions
- Group related components logically
- Use appropriate abstraction levels for each diagram type

## Integration with Documentation

These diagrams are referenced in:

- `README.md` - Architecture overview section
- `USAGE.md` - Technical implementation details
- Code comments - Component-specific architecture notes

## Tools and Dependencies

### Required for Viewing

- Web browser (for online PlantUML server)
- Java 8+ (for local PlantUML installation)
- VS Code with PlantUML extension (optional)

### Required for Editing

- Text editor with PlantUML syntax highlighting
- PlantUML preview capability
- Basic understanding of PlantUML syntax

## PlantUML Syntax Reference

For editing these diagrams, refer to:

- [PlantUML Official Documentation](https://plantuml.com/)
- [PlantUML Component Diagram Guide](https://plantuml.com/component-diagram)
- [PlantUML Activity Diagram Guide](https://plantuml.com/activity-diagram-beta)
- [PlantUML Deployment Diagram Guide](https://plantuml.com/deployment-diagram)

## Contributing

When contributing changes to the architecture:

1. Update the relevant diagram files
2. Test diagram rendering
3. Ensure consistency across all diagrams
4. Update this README if adding new diagram types
5. Include diagram updates in pull requests
