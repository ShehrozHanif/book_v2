---
name: personalization-ui
description: Build user preference panels and personalization UI components
model: sonnet
---

# Personalization UI Skill

## Purpose
Create user-friendly interfaces for managing personalization preferences, settings, and customization options.

## Key Responsibilities
- Design settings/preferences panel layouts
- Build preference toggle components
- Create form controls for customization
- Implement settings save/reset functionality
- Build preference preview functionality
- Add settings persistence
- Create settings groups/categories
- Implement settings search/filter
- Handle preference validation

## Settings Categories

### Display Preferences
- Theme (light/dark/auto)
- Font size
- Layout density (compact/normal/spacious)
- Color scheme preference
- Animation preferences (reduced motion)

### Content Preferences
- Content language
- Difficulty level
- Content filters/categories
- Featured sections
- Bookmark management

### Learning Preferences
- Learning pace (slow/normal/fast)
- Content format preferences (text/video/interactive)
- Assessment frequency
- Reminder preferences
- Progress tracking display

### Notification Preferences
- Email notifications
- Browser notifications
- Notification frequency
- Topics to follow
- Quiet hours setting

### Privacy Settings
- Data collection consent
- Analytics tracking
- Advertising preferences
- Sharing permissions
- Account visibility

## UI Components

### Settings Panel Layout
```jsx
<SettingsPanel>
  <SettingsHeader />
  <SettingsList>
    {settingsCategories.map(category => (
      <SettingsCategory key={category.id}>
        {category.items.map(item => (
          <SettingItem key={item.id}>
            <SettingControl />
          </SettingItem>
        ))}
      </SettingsCategory>
    ))}
  </SettingsList>
  <SettingsActions />
</SettingsPanel>
```

### Control Types

#### Toggle Switch
```jsx
<Toggle
  label="Dark Mode"
  value={settings.darkMode}
  onChange={(value) => updateSetting('darkMode', value)}
/>
```

#### Select Dropdown
```jsx
<Select
  label="Font Size"
  value={settings.fontSize}
  options={['small', 'medium', 'large']}
  onChange={(value) => updateSetting('fontSize', value)}
/>
```

#### Radio Button Group
```jsx
<RadioGroup
  label="Learning Pace"
  value={settings.pace}
  options={[
    { label: 'Slow', value: 'slow' },
    { label: 'Normal', value: 'normal' },
    { label: 'Fast', value: 'fast' }
  ]}
/>
```

#### Slider
```jsx
<Slider
  label="Text Size"
  min={12}
  max={20}
  value={settings.textSize}
  onChange={(value) => updateSetting('textSize', value)}
/>
```

#### Multi-select Checkbox
```jsx
<CheckboxGroup
  label="Topics"
  value={settings.topics}
  options={availableTopics}
/>
```

## State Management

```jsx
const [settings, setSettings] = useState(defaultSettings);
const [unsavedChanges, setUnsavedChanges] = useState({});
const [saving, setSaving] = useState(false);
const [saveStatus, setSaveStatus] = useState(null);
```

## Features

### Settings Organization
- Group by category
- Collapsible sections
- Search/filter functionality
- Frequently changed items at top

### Save/Reset
- Save button
- Reset to defaults button
- Unsaved changes indicator
- Confirmation dialogs

### Preview
- Live preview of changes
- Before/after comparison
- Preview in different contexts

### Import/Export
- Export settings as JSON
- Import settings file
- Backup settings

### Preset Profiles
- Save setting combinations
- Load presets
- Manage custom presets

## State Persistence

```jsx
// Save to localStorage
const saveSettings = async (newSettings) => {
  setSaving(true);
  try {
    // API call to backend
    await updateUserSettings(newSettings);
    // Local storage backup
    localStorage.setItem('userSettings', JSON.stringify(newSettings));
    setSettings(newSettings);
    setSaveStatus('saved');
  } catch (error) {
    setSaveStatus('error');
  }
  setSaving(false);
};
```

## Validation

```jsx
const validateSettings = (newSettings) => {
  const errors = {};

  if (newSettings.fontSize < 12 || newSettings.fontSize > 20) {
    errors.fontSize = 'Font size must be between 12 and 20';
  }

  return Object.keys(errors).length === 0;
};
```

## Responsive Design
- Mobile: Stacked layout
- Tablet: Two-column layout
- Desktop: Sidebar + content
- Modals for small screens

## Accessibility Features
- Proper labels for all controls
- ARIA descriptions
- Keyboard navigation
- Focus management
- Screen reader support
- Color contrast compliance
- Sufficient click targets

## Performance Considerations
- Debounce settings updates
- Only save changed values
- Lazy load preference panels
- Cache user preferences
- Implement settings versioning

## Integration Points
- Connect to user profile API
- Sync across devices
- Real-time preference updates
- Theme system integration
- Content filtering integration
