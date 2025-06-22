# ION Navigator Design System

## Overview
This design system provides a comprehensive set of components, colors, and utilities for building professional interfaces in the ION Navigator application. The system is built around the University of Delaware's brand colors: Delaware Blue and Delaware Gold.

## Color Palette

### Primary Colors
- **Delaware Blue**: `#00539F` (Primary actions, headers, links)
- **Delaware Blue Dark**: `#003366` (Text, emphasis)
- **Delaware Blue Light**: `#E6F3FF` (Backgrounds, hover states)
- **Delaware Blue Hover**: `#0066CC` (Interactive states)

### Secondary Colors
- **Delaware Gold**: `#FFD200` (Accent buttons, highlights)
- **Delaware Gold Dark**: `#E6BD00` (Text on gold backgrounds)
- **Delaware Gold Light**: `#FFF8CC` (Light backgrounds)
- **Delaware Gold Hover**: `#FFDC33` (Interactive states)

### Semantic Colors
- **Success**: `#28A745` (Success states, completed actions)
- **Warning**: `#FFC107` (Warning states, pending actions)
- **Error**: `#DC3545` (Error states, failed actions)
- **Info**: Delaware Blue (Information, neutral states)

## Typography

### Font Family
- **Primary**: Inter (Professional, readable)
- **Monospace**: Monaco, Menlo, Ubuntu Mono

### Font Sizes
- **xs**: 12px (Small text, captions)
- **sm**: 14px (Body text, labels)
- **base**: 16px (Default body text)
- **lg**: 18px (Subheadings)
- **xl**: 20px (Small headings)
- **2xl**: 24px (Medium headings)
- **3xl**: 32px (Large headings)
- **4xl**: 40px (Display headings)

### Font Weights
- **Normal**: 400 (Regular text)
- **Medium**: 500 (Emphasized text)
- **Semibold**: 600 (Subheadings)
- **Bold**: 700 (Headings)

## Spacing System
Based on 8px grid system:
- **xs**: 4px
- **sm**: 8px
- **md**: 16px
- **lg**: 24px
- **xl**: 32px
- **2xl**: 48px
- **3xl**: 64px

## Components

### Buttons
```css
.btn                 /* Base button styles */
.btn-primary         /* Delaware Blue button */
.btn-secondary       /* Delaware Gold button */
.btn-outline-primary /* Outlined primary button */
.btn-ghost           /* Text-only button */
.btn-success         /* Success button */
.btn-warning         /* Warning button */
.btn-danger          /* Danger button */

/* Button Sizes */
.btn-sm              /* Small button (32px height) */
.btn-lg              /* Large button (48px height) */
.btn-xl              /* Extra large button (56px height) */
```

### Cards
```css
.card                /* Base card container */
.card-header         /* Card header section */
.card-body           /* Card main content */
.card-footer         /* Card footer section */
.card-title          /* Card title */
.card-subtitle       /* Card subtitle */
.card-text           /* Card body text */
```

### Status Badges
```css
.status-badge        /* Base badge styles */
.status-badge-success    /* Success badge */
.status-badge-warning    /* Warning badge */
.status-badge-error      /* Error badge */
.status-badge-info       /* Info badge */
.status-badge-neutral    /* Neutral badge */
```

### Forms
```css
.form-group          /* Form field container */
.form-label          /* Form field label */
.form-control        /* Form input/textarea/select */
```

### Tables
```css
.table               /* Base table styles */
.table-striped       /* Striped table rows */
```

### Loading Components
```css
.loading-spinner     /* Circular loading spinner */
.loading-spinner-lg  /* Large spinner */
.loading-spinner-sm  /* Small spinner */
.loading-overlay     /* Full-screen loading overlay */
.skeleton            /* Skeleton loading animation */
.dot-loader          /* Pulsing dot loader */
.progress-loading    /* Animated progress bar */
```

## Utility Classes

### Colors
```css
.text-primary        /* Delaware Blue text */
.text-secondary      /* Delaware Gold text */
.text-success        /* Success text color */
.text-warning        /* Warning text color */
.text-danger         /* Error text color */
.text-muted          /* Muted text color */

.bg-primary          /* Delaware Blue background */
.bg-secondary        /* Delaware Gold background */
.bg-light           /* Light gray background */
```

### Layout
```css
.d-flex              /* Display flex */
.d-inline-flex       /* Display inline-flex */
.d-block             /* Display block */
.d-none              /* Display none */

.justify-content-center    /* Center justify content */
.justify-content-between   /* Space between justify */
.justify-content-end       /* End justify content */

.align-items-center        /* Center align items */
.align-items-start         /* Start align items */
.align-items-end           /* End align items */
```

### Spacing
```css
.gap-sm              /* Small gap (8px) */
.gap-md              /* Medium gap (16px) */
.gap-lg              /* Large gap (24px) */

.p-sm                /* Small padding */
.p-md                /* Medium padding */
.p-lg                /* Large padding */

.m-sm                /* Small margin */
.m-md                /* Medium margin */
.m-lg                /* Large margin */
```

### Shadows
```css
.shadow-sm           /* Small shadow */
.shadow-md           /* Medium shadow */
.shadow-lg           /* Large shadow */
```

## Usage Examples

### Professional Button
```jsx
<button className="btn btn-primary btn-lg">
  <span>Analyze Trace</span>
  <Icon />
</button>
```

### Status Badge
```jsx
<span className="status-badge status-badge-success">
  Completed
</span>
```

### Loading State
```jsx
<div className="loading-overlay">
  <div className="loading-content">
    <div className="loading-spinner loading-spinner-lg"></div>
    <div className="loading-text">Processing your trace...</div>
  </div>
</div>
```

### Professional Card
```jsx
<div className="card">
  <div className="card-header">
    <h3 className="card-title">Trace Analysis</h3>
    <p className="card-subtitle">Performance Insights</p>
  </div>
  <div className="card-body">
    <p className="card-text">Analysis results...</p>
  </div>
  <div className="card-footer">
    <button className="btn btn-primary">View Details</button>
  </div>
</div>
```

## Responsive Design
The design system includes responsive breakpoints:
- **sm**: 576px
- **md**: 768px
- **lg**: 992px
- **xl**: 1200px
- **2xl**: 1400px

## Accessibility
- All interactive elements have proper focus states
- Color contrast ratios meet WCAG AA standards
- Semantic HTML structure is maintained
- Keyboard navigation is supported

## Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Grid and Flexbox support required
- CSS Custom Properties (variables) support required

## Implementation Phases

### Phase 1: Global Design System ✅
**Files**: `variables.css`, `components.css`, `loading.css`, existing component updates

1. **CSS Variables System**: Delaware color palette, typography scale, spacing system
2. **Component Library**: Buttons, cards, forms, status badges, tables, utilities
3. **Loading Components**: Spinners, skeleton loading, progress indicators
4. **Enhanced Components**: Top Banner, Trace Table, Homepage with professional styling

### Phase 2: Detail Views & Chat Interface ✅
**Files**: `ChatWindow.css`, `DiagnosisTree.css`, `AuthModal.css`

1. **Chat Window**: Professional chat interface with Delaware Blue header, message bubbles, markdown rendering, feedback system, and responsive design
2. **Diagnosis Tree**: Interactive tree visualization with professional node styling, zoom controls, content modals, and step-based color coding
3. **Authentication Modal**: Delaware-themed login/signup with gradient header, professional forms, smooth animations, and mobile optimization

### Phase 3: Data Visualization & Advanced Components ✅
**Files**: `FileUpload.css`, `Notifications.css`, `Dashboard.css`, `AdvancedTable.css`, `DataVisualization.css`

1. **File Upload**: Professional drag-and-drop upload component with progress tracking, file validation, and status indicators
2. **Notification System**: Comprehensive toast messages, alert banners, inline notifications, and status indicators with auto-dismiss and positioning options
3. **Dashboard Components**: Metrics cards, status dashboards, activity feeds, quick stats with professional styling and responsive layouts
4. **Advanced Tables**: Enhanced table features including sorting, filtering, pagination, search, column resizing, and row selection
5. **Data Visualization**: Chart containers, performance metrics, mini charts, progress rings, heatmaps, and tooltips with Delaware theme integration

## File Structure
```
src/styles/
├── variables.css          # Design tokens and CSS variables
├── components.css         # Reusable component library
├── loading.css           # Loading states and animations
├── ChatWindow.css        # Chat interface styling
├── DiagnosisTree.css     # Tree visualization styling
├── AuthModal.css         # Authentication modal styling
├── TopBanner.css         # Top navigation styling
├── TraceTable.css        # Data table styling
├── HomePage.css          # Homepage layout styling
├── FileUpload.css        # File upload components
├── Notifications.css     # Notification system
├── Dashboard.css         # Dashboard components
├── AdvancedTable.css     # Advanced table features
├── DataVisualization.css # Charts and data visualization
└── README.md            # This documentation
``` 