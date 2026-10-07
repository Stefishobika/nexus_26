# HNX26 – Autonomous Vision & Behaviour Understanding

## Factory Safety Monitoring System

An AI-powered computer vision system for monitoring worker safety in factory environments. The system detects and tracks workers, identifies PPE (Personal Protective Equipment) violations, monitors dangerous machine zones, and generates meaningful safety events based on worker location and duration.

---

## 1. Project Overview

Factory environments contain several safety risks, including proximity to machinery and failure to wear appropriate protective equipment.

This project provides an automated video-based safety monitoring system that analyzes factory surveillance footage and detects potentially unsafe situations.

The system combines:

- Person detection
- Person tracking
- PPE detection
- Danger-zone monitoring
- Time-based safety analysis
- Fall detection
- Safety event identification
- Web-based visualization

Instead of simply detecting objects, the system attempts to understand **what is happening, which person is involved, and when the event occurs**.

### Example Safety Events

The system can identify events such as:

- Person entering a machine danger zone
- Person remaining in a danger zone for more than the allowed duration
- Missing hardhat
- Missing gloves
- Missing goggles/eye protection
- Missing mask
- Missing safety vest
- Fall detection

---

# 2. System Workflow

```text
                    Factory Video
                          |
                          v
                  +----------------+
                  |     YOLO11     |
                  | Person Detection|
                  +--------+-------+
                           |
                           v
                    +-------------+
                    |  ByteTrack  |
                    |   Tracking  |
                    +------+------+
                           |
                           v
                  Persistent Person IDs
                           |
             +-------------+-------------+
             |                           |
             v                           v
      Danger Zone Analysis          PPE Detection
             |                           |
             v                           v
      Position + Duration          Safety Equipment
             |                    / Violations
             |                           |
             +-------------+-------------+
                           |
                           v
                    Safety Events
                           |
                           v
                   Flask Backend
                           |
                           v
                HTML + CSS + JavaScript
                           |
                           v
                   Safety Dashboard
