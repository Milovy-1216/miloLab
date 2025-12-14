import csv
import os

def time_to_frame_string(seconds, fps=24):
    """Convert seconds to HH:MM:SS:FF format."""
    total_frames = int(seconds * fps)
    ff = total_frames % fps
    total_seconds = total_frames // fps
    ss = total_seconds % 60
    total_minutes = total_seconds // 60
    mm = total_minutes % 60
    hh = total_minutes // 60
    return f"{hh:02}:{mm:02}:{ss:02}:{ff:02}"

def export_to_csv_markers(timestamps, output_path, fps=24):
    """
    Export timestamps to a CSV file compatible with Adobe Premiere Pro Markers.
    Format: Marker Name, Description, In, Out, Duration, Marker Type
    """
    header = ["Marker Name", "Description", "In", "Out", "Duration", "Marker Type"]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t') # Premiere often prefers tab-delimited for markers, or CSV. Let's try standard CSV first but Premiere markers are tricky. Actually, standard CSV is safest, but Premiere export is usually tab. Let's stick to standard CSV structure but check delimiter.
        # Re-reading: Premiere Pro CSV markers are usually comma separated but the header is specific.
        # Let's use standard comma.
        writer = csv.writer(f)
        writer.writerow(header)
        
        for i, t in enumerate(timestamps):
            time_code = time_to_frame_string(t, fps)
            # Name, Desc, In, Out, Dur, Type
            writer.writerow([f"Beat {i+1}", "Beat", time_code, time_code, "00:00:00:00", "Comment"])

def export_to_edl(timestamps, output_path, title="BEAT_TRACK", fps=24):
    """
    Export timestamps to CMX 3600 EDL.
    Each beat is a cut.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"TITLE: {title}\n")
        f.write("FCM: NON-DROP FRAME\n\n")
        
        for i, t in enumerate(timestamps):
            # EDL format:
            # 001  AX       V     C        00:00:00:00 00:00:00:01 00:00:05:00 00:00:05:01
            # Event Num, Reel, Channel, Type, Src In, Src Out, Rec In, Rec Out
            
            event_num = f"{i+1:03}"
            reel = "AX"
            channel = "V"
            trans = "C"
            
            # For a beat marker, we effectively want a cut or a placeholder.
            # In EDL, we map the "Record In" to the beat time.
            # We'll make each "clip" 1 frame long for visibility.
            
            rec_in_sec = t
            rec_out_sec = t + (1/fps)
            
            rec_in = time_to_frame_string(rec_in_sec, fps)
            rec_out = time_to_frame_string(rec_out_sec, fps)
            
            # Source time doesn't matter much for a placeholder, but let's keep it 0
            src_in = "00:00:00:00"
            src_out = "00:00:00:01"
            
            line = f"{event_num}  {reel:<8} {channel:<5} {trans:<8} {src_in} {src_out} {rec_in} {rec_out}\n"
            f.write(line)
            f.write("\n") # Blank line often required between events or just good practice


def export_to_fcpxml(timestamps, output_path, fps=24, duration_seconds=600):
    """
    Export timestamps to FCPXML (Final Cut Pro XML).
    Creates a gap clip with markers.
    """
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    # FCPXML structure
    fcpxml = ET.Element("fcpxml", version="1.9")
    resources = ET.SubElement(fcpxml, "resources")
    format_elem = ET.SubElement(resources, "format", id="r1", name=f"FFVideoFormat{fps}p", 
                                frameDuration=f"1/{fps}s", width="1920", height="1080")
    
    library = ET.SubElement(fcpxml, "library")
    event = ET.SubElement(library, "event", name="Beat Markers")
    project = ET.SubElement(event, "project", name="Beat Track")
    sequence = ET.SubElement(project, "sequence", format="r1")
    spine = ET.SubElement(sequence, "spine")
    
    # Create a gap clip that spans the whole duration (or arbitrary long if unknown, but better to be precise)
    # We'll default to a long duration if not provided, or max beat time
    if len(timestamps) > 0:
        max_time = max(timestamps)
        if max_time > duration_seconds:
            duration_seconds = max_time + 10
            
    total_frames = int(duration_seconds * fps)
    gap = ET.SubElement(spine, "gap", name="Gap", offset="0s", duration=f"{total_frames}/{fps}s", start="0s")
    
    for i, t in enumerate(timestamps):
        # FCPXML markers use rational time: "frame/fps s"
        frame = int(t * fps)
        marker_start = f"{frame}/{fps}s"
        
        # Add marker to the gap clip
        ET.SubElement(gap, "marker", start=marker_start, duration=f"1/{fps}s", value=f"Beat {i+1}")

    # Write to file
    xmlstr = minidom.parseString(ET.tostring(fcpxml)).toprettyxml(indent="    ")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xmlstr)
