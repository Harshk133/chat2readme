# Generated Documentation

# Problem

My gun is not aligned with the camera in FPS view

# Root Cause

This happens because the weapon uses world coordinates

# Solution

Attach the weapon to the camera

# Implementation

```
weapon.parent = camera
```

# Notes

Now the camera alignment works correctly
