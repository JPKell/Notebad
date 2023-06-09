# Events

Events drive the communication between the view and the app. This should be updated anytime a new event is added

Events are described by their sequence, the text between the `<< >>`
There is a generator and if it matters it will be described, otherwise it can come from anywhere. 

# IDE/Text events
- `<<Undo>>`
  - Generator: ide
  - Handler: ide.history.undo

- `<<Redo>>`
  - Generator: ide
  - Handler: ide.history.undo

- `<<Paste>>`
  - Generator: ide
  - Handler: ide.clipboard.paste

- `<<FindFocus>>`
  - Generator: ide
  - toolbar.find_entry.focus_set()

- `<<FindNext>>`, `<<FindPrev>>`
  - Generator: ide
  - Handler: ide.editor.find_next(direction = 1 | -1 )

# Global events

## Profiler
- `<<ProfilerFileChanged>>` 
    - Handler: self.parse_progress_profiler
- `<<ProfilerSourceView>>`  
    - Handler: self.build_profiler_source

## Window events
- `<<OpenKeyCommandList>>`  
    - Handler: self.populate_key_commands
- `<<OpenCalculator>>`      
    - Handler: self.utilities.open_calculator
- `<<ExitApp>>`             
    - Handler: self.exit_app

## File management events
- `<<NewFile>>`             
  - Generator: Any
  - Handler: self.file_system.new_file
  
- `<<OpenFile>>`            
  - Generator: NTabFrame, NFrame
  - Handler: self.file_system.open_file

- `<<OpenRecentFile>>` 
  - Generator: view.menu     
  - Handler: self.file_system.open_recent_file

- `<<SaveFile>>`            
  - Generator: NTabFrame, NFrame
  - Handler: self.file_system.save_file

- `<<SaveFileAs>>`          
  - Generator: NTabFrame, NFrame
  - Handler: self.file_system.save_file_as

## UI Events
- `<<ThemeToggle>>`
  - Handler: Widgets typically have a method. This should get unified across widgets

## Language events

## Nifty
- `<<PyEvalLine>>`         
  - self.utilities.eval_selection  