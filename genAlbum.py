import os
from PIL import Image
from PIL.ExifTags import TAGS
import calendar
from datetime import datetime


def extract_image_date(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()

        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == 'DateTimeOriginal':  # Date when the photo was taken
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    # If EXIF data is not available, fallback to file's modification time
    file_time = os.path.getmtime(file_path)
    return datetime.fromtimestamp(file_time)


def generate_photo_album(root_folder):
    # Dictionary to group images by year-month
    photo_groups = {}
    processed_files = 0
    total_files = sum([len([file for file in files if file.lower().endswith(
        ('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]) for _, _, files in
                       os.walk(root_folder)])
    # Walk through the folder and gather images
    for root, _, files in os.walk(root_folder):
        for file in files:

            # Update progress
            processed_files += 1
            progress = processed_files / total_files
            progress_bar = (u"\u2588" * int(progress * 40)).ljust(40)
            print(f"\r{progress_bar} {progress * 100:.2f}%", end='')

            if "resized" not in file:
                continue
            #print(file)
            if file.lower().endswith(('jpg', 'jpeg', 'png')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_folder)
                image_date = extract_image_date(file_path)

                # Group by year-month
                year_month = image_date.strftime('%Y-%m')
                if year_month not in photo_groups:
                    photo_groups[year_month] = []
                photo_groups[year_month].append(rel_path)

    # Generate HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Photo Album</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }
            header {
                background-color: #4285f4;
                color: white;
                padding: 10px;
                text-align: center;
                font-size: 24px;
            }
            .timeline {
                width: 100%;
                background: #e0e0e0;
                padding: 20px;
                box-sizing: border-box;
            }
            .timeline-item {
                margin-bottom: 40px;
            }
            .timeline-date {
                font-size: 20px;
                color: #333;
                margin-bottom: 10px;
            }
            .photo-grid {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .photo-grid img {
                width: 200px;
                height: 200px;
                object-fit: cover;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                opacity: 1;
                transition: opacity 0.3s;
                cursor: pointer;
            }
            .photo-grid img.lazy {
                opacity: 0;
            }
            .photo-grid img.lazy.lazyloaded {
                opacity: 1;
            }
            /* Modal styles */
            #myModal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.8);
                justify-content: center;
                align-items: center;
            }
            #modal-content {
                max-width: 90%;
                max-height: 90%;
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
            }
            #modal-content img {
                max-width: 90vw;
                max-height: 90vh;
                object-fit: contain;
                border-radius: 8px;
            }
            .close {
                position: absolute;
                top: 20px;
                right: 30px;
                color: white;
                font-size: 30px;
                font-weight: bold;
                cursor: pointer;
            }
            .close:hover {
                color: #bbb;
            }
            /* Previous and Next buttons */
            .prev, .next {
                cursor: pointer;
                position: absolute;
                top: 50%;
                width: auto;
                margin-top: -22px;
                padding: 16px;
                color: white;
                font-weight: bold;
                font-size: 24px;
                transition: 0.3s;
                border-radius: 0 3px 3px 0;
                user-select: none;
            }
            .next {
                right: 0;
                border-radius: 3px 0 0 3px;
            }
            .prev {
                left: 0;
            }
            .prev:hover, .next:hover {
                background-color: rgba(0,0,0,0.8);
            }
             /* Scrollbar navigation */
             
            /* custom scrollbar */
            ::-webkit-scrollbar {
              width: 20px;
            }
            
            ::-webkit-scrollbar-track {
              background-color: transparent;
            }
            
            ::-webkit-scrollbar-thumb {
              background-color: #d6dee1;
              border-radius: 20px;
              border: 6px solid transparent;
              background-clip: content-box;
            }
            
            ::-webkit-scrollbar-thumb:hover {
              background-color: #a8bbbf;
            }
             
            .scrollbar {
                position: fixed;
                top: 50%;
                right: 10px;
                transform: translateY(-50%);
                width: 100px;
                max-height: 70%; /* Max height for the scrollbar */
                overflow-y: auto; /* Make it scrollable */
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                padding: 10px;
                opacity: .6;
            }
            .year-bullet {
                width: 30px;
                height: 20px;
                background-color: #4285f4;
                /*border-radius: 50%;*/
                cursor: pointer;
                transition: background-color 0.3s;
            }
            
            .month-bullet {
                width: 15px;
                height: 20px;
                background-color: #4285f4;
                /*border-radius: 50%;*/
                cursor: pointer;
                transition: background-color 0.5s;
            }
            .year-bullet:hover, .month-bullet:hover {
                background-color: #ff5722;
            }
            .scrollbar-text {
                font-size: 14px;
                color: #000000;
                margin-left: 10px;
            }
            .scrollbar-month-text {
                font-size: 12px;
                color: #000000;
                margin-left: 10px;
            }
            .scrollbar-item {
                display: flex;
                align-items: center;
            }
        </style>
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                var lazyImages = [].slice.call(document.querySelectorAll("img.lazy"));
                var imagePaths = []; // Array to hold all image paths
                var currentIndex = 0; // Track the current index for navigation

                document.querySelectorAll(".photo-grid img").forEach(function(img, index) {
                    let src = img.src || img.dataset.src;
                    if (src) {
                        src = src.replace('-resized', '');
                    }
                    imagePaths.push(src);
       
                });

                if ("IntersectionObserver" in window) {
                    let lazyImageObserver = new IntersectionObserver(function(entries, observer) {
                        entries.forEach(function(entry) {
                            if (entry.isIntersecting) {
                                let lazyImage = entry.target;
                                lazyImage.src = lazyImage.dataset.src;
                                lazyImage.classList.add("lazyloaded");
                                lazyImageObserver.unobserve(lazyImage);
                            }
                        });
                    });
                    lazyImages.forEach(function(lazyImage) {
                        lazyImageObserver.observe(lazyImage);
                    });
                }
                
                // Scroll to specific year or month
                function scrollToElement(id) {
                    document.getElementById(id).scrollIntoView({
                        behavior: 'smooth'
                    });
                }

                // Add event listeners to bullets
                document.querySelectorAll('.year-bullet, .month-bullet').forEach(function(bullet) {
                    bullet.addEventListener('click', function() {
                        const target = bullet.getAttribute('data-target');
                        scrollToElement(target);
                    });
                });

                // Modal functionality
                var modal = document.getElementById("myModal");
                var modalImg = document.getElementById("modal-img");
                var closeModal = document.getElementsByClassName("close")[0];
                var prevBtn = document.getElementsByClassName("prev")[0];
                var nextBtn = document.getElementsByClassName("next")[0];

                // Function to open the modal with the clicked image
                function openModal(index) {
                    currentIndex = index;
                    modal.style.display = "flex";
                    modalImg.src = imagePaths[currentIndex];  // Load full-size image in the modal
                }

                // Attach click event to both eager and lazy-loaded images
                document.querySelectorAll(".photo-grid img").forEach((img, index) => {
                    img.addEventListener("click", function() {
                        openModal(index); // Open modal with clicked image
                    });
                });

                // Close modal
                closeModal.onclick = function() {
                    modal.style.display = "none";
                };

                // Previous image
                prevBtn.onclick = function() {
                    currentIndex = (currentIndex - 1 + imagePaths.length) % imagePaths.length;
                    modalImg.src = imagePaths[currentIndex];
                };

                // Next image
                nextBtn.onclick = function() {
                    currentIndex = (currentIndex + 1) % imagePaths.length;
                    modalImg.src = imagePaths[currentIndex];
                };
                
                // Handle keyboard navigation
                document.addEventListener('keydown', function(event) {
                    if (event.key === 'ArrowLeft') {
                        // Left arrow key pressed
                        currentIndex = (currentIndex - 1 + imagePaths.length) % imagePaths.length;
                        modalImg.src = imagePaths[currentIndex];
                    } else if (event.key === 'ArrowRight') {
                        // Right arrow key pressed
                        currentIndex = (currentIndex + 1) % imagePaths.length;
                        modalImg.src = imagePaths[currentIndex];
                    } 
                });

                // Close the modal when clicking outside of the image
                window.onclick = function(event) {
                    if (event.target == modal) {
                        modal.style.display = "none";
                    }
                };
            });

        </script>
    </head>
    <body>
        <header>
            Photo Album Timeline
        </header>
        <div class="timeline">
    """
    scrollbar_content = '<div class="scrollbar">'
    # Loop over each group and generate HTML for it
    first_load_count = 0
    current_year = None
    max_initial_load = 12  # Number of images to eagerly load initially
    for year_month, images in sorted(photo_groups.items(), reverse=True):
        #print(year_month)
        year, month = year_month.split('-')

        # Add a bullet for each year
        if year != current_year:
            current_year = year
            scrollbar_content += f'''
            <div class="scrollbar-item">
                <div class="year-bullet" data-target="year-{year}"></div>
                <span class="scrollbar-text">{year}</span>
            </div>
            '''

        # Add smaller bullet for each month under that year
        scrollbar_content += f'''
        <div class="scrollbar-item">
            <div class="month-bullet" data-target="month-{year_month}"></div>
            <span class="scrollbar-month-text">{month}</span>
        </div>
        '''
        mon_name = calendar.month_name[int(month)]
        html_content += f'<div class="timeline-item" id="month-{year_month}">'
        html_content += f'<div class="timeline-date" id="year-{year}">{year} {mon_name}</div>'
        html_content += f'<div class="photo-grid">'

        for image_path in images:
            if first_load_count < max_initial_load:
                # Eagerly load the first few images
                html_content += f'<img src="{image_path}" alt="Photo">'
            else:
                # Lazy load remaining images using 'data-src'
                html_content += f'<img class="lazy" data-src="{image_path}" alt="Photo">'
            first_load_count += 1

        html_content += f'</div></div>'
    scrollbar_content += '</div>'  # Close scrollbar div

    # Add modal HTML with navigation buttons
    html_content += """
        </div>
        <!-- Scrollbar with clickable bullets -->
        """ + scrollbar_content + """
        <!-- The Modal -->
        <div id="myModal" class="modal">
            <span class="close">&times;</span>
            <div id="modal-content">
                <span class="prev">&#10094;</span>
                <img id="modal-img" src="" alt="Large photo">
                <span class="next">&#10095;</span>
            </div>
        </div>
    </body>
    </html>
    """

    # Save the HTML file with UTF-8 encoding
    output_file = os.path.join(root_folder, 'photo_album.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nPhoto album generated at: {output_file}")

# Example usage
if __name__ == "__main__":
    root_folder = "E:/TakeoutMerge"  #input("Enter the path to the folder containing your photos: ")
    generate_photo_album(root_folder)
