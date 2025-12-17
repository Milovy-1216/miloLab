document.addEventListener('DOMContentLoaded', () => {

    /* =========================================
       1. Hero Scroll Effect (Gauguin -> Real)
       ========================================= */
    const gauguinBg = document.getElementById('bg-gauguin');
    const heroSection = document.getElementById('hero');
    const videoSection = document.getElementById('opening-video'); // Get video section

    // Recalculate heights on resize if needed, but for now just get them

    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY;
        const videoHeight = videoSection ? videoSection.offsetHeight : 0;

        // Logical Scroll for Hero: 
        // 0 when at top of Hero (which is at videoHeight)
        const effectiveScroll = scrollY - videoHeight;

        // If we haven't reached the hero yet (still in video), opacity stays 1
        // (Wait, opacity logic: 1 -> 0. so initially it should be 1? 
        // Gauguin is the first image seen IN the hero. It fades to reveal "Real".
        // So yes, it should stay 1 (Opaque) until we start scrolling inside Hero.)

        if (effectiveScroll < 0) {
            if (gauguinBg) gauguinBg.style.opacity = 1;
            return;
        }

        // Calculate opacity: 1 at top of Hero, 0 at 100% of Viewport Height into Hero
        let opacity = 1 - (effectiveScroll / (window.innerHeight * 1.2));

        if (opacity < 0) opacity = 0;
        if (opacity > 1) opacity = 1;

        if (gauguinBg) {
            gauguinBg.style.opacity = opacity;
        }
    });

    /* =========================================
       2. Ambient Sound
       ========================================= */
    // Ambient Sound Logic
    let currentAudio = null; // Track currently playing audio

    // Create Audio instances (Simulated/Placeholder)
    const sounds = {
        'market-noise': new Audio('https://actions.google.com/sounds/v1/ambiences/coffee_shop.ogg'), // Placeholder
        'chopping': new Audio('https://actions.google.com/sounds/v1/foley/cutting_on_cutting_board.ogg'), // Placeholder
        'water': new Audio('https://actions.google.com/sounds/v1/water/air_woosh_underwater.ogg') // Placeholder
    };

    // Helper to toggle sound
    window.toggleSound = function (soundKey, btn) {
        const audio = sounds[soundKey];
        if (!audio) return;

        if (!audio.paused) {
            audio.pause();
            btn.innerHTML = '🔊 播放環境音';
            btn.classList.remove('playing');
        } else {
            // Stop others
            Object.values(sounds).forEach(s => s.pause());
            document.querySelectorAll('.audio-btn').forEach(b => {
                b.innerHTML = '🔊 播放環境音'; // Reset all buttons
                b.classList.remove('playing');
            });

            audio.currentTime = 0;
            audio.play();
            btn.innerHTML = '🔇 停止音效';
            btn.classList.add('playing');
            currentAudio = audio;
        }
    };


    /* =========================================
       3. Data Viz Animation
       ========================================= */
    const progressBars = document.querySelectorAll('.progress-bar-fill');

    // Observer for animation trigger
    const vizObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const targetWidth = entry.target.getAttribute('data-width');
                entry.target.style.width = targetWidth;
            }
        });
    }, { threshold: 0.5 });

    progressBars.forEach(bar => vizObserver.observe(bar));


    /* =========================================
       4. Wish Wall (CTA)
       ========================================= */
    const wishForm = document.getElementById('wish-form');
    const wishWall = document.getElementById('wish-wall');
    const wishText = document.getElementById('wish-text');

    if (wishForm) {
        wishForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const text = wishText.value.trim();
            if (text) {
                const note = document.createElement('div');
                note.classList.add('wish-note');
                note.innerText = text;

                // Add randomly slightly different rotation for natural look
                const rot = (Math.random() * 6) - 3;
                note.style.transform = `rotate(${rot}deg)`;

                wishWall.appendChild(note);
                wishText.value = '';

                // Optional: Scroll to bottom of wall
                note.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    /* =========================================
       5. Navigation Scroll Spy
       ========================================= */
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = [
        document.getElementById('chapter-1'),
        document.getElementById('chapter-2'),
        document.getElementById('chapter-3')
    ];

    window.addEventListener('scroll', () => {
        let current = '';
        const scrollPosition = window.scrollY + (window.innerHeight / 3); // Trigger point

        sections.forEach(section => {
            if (section) {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;

                // Check if we are within this section
                if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                    current = section.getAttribute('id');
                }
            }
        });

        // Special case: If near bottom, activate last Chapter
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 50) {
            current = 'chapter-3';
        }

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.target === current) {
                link.classList.add('active');
            }
        });
    });

    /* =========================================
    /* =========================================
       6. Chapter 2 Intro Animation (Scale & Fade)
       ========================================= */
    const introWrapper = document.getElementById('chapter-2-intro');
    const vendorIcon = document.getElementById('icon-vendor');
    const consumerIcon = document.getElementById('icon-consumer');
    const committeeIcon = document.getElementById('icon-committee');

    if (introWrapper && vendorIcon && consumerIcon && committeeIcon) {
        window.addEventListener('scroll', () => {
            const rect = introWrapper.getBoundingClientRect();
            const wrapperHeight = introWrapper.offsetHeight;
            const windowHeight = window.innerHeight;

            // Start: rect.top <= 0
            // End: rect.bottom <= windowHeight

            if (rect.top <= 0 && rect.bottom >= windowHeight) {
                // We are in the active sticky zone
                const scrolled = Math.abs(rect.top); // Pixels scrolled into the section
                const totalScrollable = wrapperHeight - windowHeight;
                let progress = scrolled / totalScrollable;

                if (progress < 0) progress = 0;
                if (progress > 1) progress = 1;

                // Animation Logic
                // 1. Vendor Icon Scales Up (1 -> 5 or more to fill screen)
                const scale = 1 + (progress * 2);

                vendorIcon.style.transform = `scale(${scale})`;

                // 2. Others Fade Out (1 -> 0)
                const opacity = 1 - (progress * 2); // Fade out faster (first 50%)
                const safeOpacity = opacity < 0 ? 0 : opacity;

                consumerIcon.style.opacity = safeOpacity;
                committeeIcon.style.opacity = safeOpacity;

                // Optional: Fade out text as well to keep focus on Vendor
                const textOpacity = 1 - (progress * 3);
                const introText = document.querySelector('.intro-text');
                if (introText) introText.style.opacity = textOpacity < 0 ? 0 : textOpacity;

            } else if (rect.top > 0) {
                // Reset (Before section)
                vendorIcon.style.transform = 'scale(1)';
                consumerIcon.style.opacity = 1;
                committeeIcon.style.opacity = 1;
                const introText = document.querySelector('.intro-text');
                if (introText) introText.style.opacity = 1;

            } else {
                // After section (Keep final state)
                vendorIcon.style.transform = 'scale(3)'; // Max scale
                consumerIcon.style.opacity = 0;
                committeeIcon.style.opacity = 0;
                const introText = document.querySelector('.intro-text');
                if (introText) introText.style.opacity = 0;
            }
        });
    }

    /* =========================================
       7. Chapter 1 Scrollytelling (Text -> Image)
       ========================================= */
    const storyWrappers = [
        { wrapper: document.getElementById('chapter-1-part-a'), bg: document.getElementById('bg-c1-a'), fg: document.getElementById('fg-c1-a') },
        { wrapper: document.getElementById('chapter-1-part-b'), bg: document.getElementById('bg-c1-b'), fg: document.getElementById('fg-c1-b') }
    ];

    window.addEventListener('scroll', () => {
        const windowHeight = window.innerHeight;

        storyWrappers.forEach(item => {
            if (!item.wrapper || !item.bg || !item.fg) return;

            const rect = item.wrapper.getBoundingClientRect();
            const wrapperHeight = item.wrapper.offsetHeight;

            // Logic: 
            // 0% -> 30%: Text fully visible, BG hidden
            // 30% -> 80%: Text fades out, BG fades in
            // 80% -> 100%: Text hidden, BG fully visible

            if (rect.top <= 0 && rect.bottom >= windowHeight) {
                // In view
                const scrolled = Math.abs(rect.top);
                const totalScrollable = wrapperHeight - windowHeight;
                let progress = scrolled / totalScrollable;

                if (progress < 0) progress = 0;
                if (progress > 1) progress = 1;

                // Opacity Control
                // Text: 1 at start, starts fading at 0.2, gone by 0.6
                let textOpacity = 1;
                if (progress > 0.2) {
                    textOpacity = 1 - ((progress - 0.2) / 0.4); // 0.4 span
                }
                if (textOpacity < 0) textOpacity = 0;

                // BG: 0 at start, starts appearing at 0.3, full by 0.8
                let bgOpacity = 0;
                if (progress > 0.3) {
                    bgOpacity = (progress - 0.3) / 0.5; // 0.5 span
                }
                if (bgOpacity > 1) bgOpacity = 1;
                if (bgOpacity < 0) bgOpacity = 0;

                item.fg.style.opacity = textOpacity;
                item.bg.style.opacity = bgOpacity;

            } else if (rect.top > 0) {
                // Before
                item.fg.style.opacity = 1;
                item.bg.style.opacity = 0;
            } else {
                // After
                item.fg.style.opacity = 0;
                item.bg.style.opacity = 1;
            }
        });
    });

    /* =========================================
       8. Chapter 1 Section C (Pure CSS Sticky Scrollytelling)
       ========================================= */

    /* =========================================
       8. Consumer Section: Horizontal Pin & Scroll
       ========================================= */
    const pinContainer = document.getElementById('consumer-pin-container');
    const track = document.getElementById('consumer-track');

    if (pinContainer && track) {
        window.addEventListener('scroll', () => {
            // Use getBoundingClientRect logic to handle finding position relative to viewport
            // The container is 400vh tall.
            // We want the horizontal scroll to happen as we move through this container.

            const rect = pinContainer.getBoundingClientRect();
            // rect.top is position of top of container relative to viewport top.

            // Start of interaction: when rect.top <= 0 (Container hits top of screen)
            // End of interaction: when rect.bottom <= windowHeight (Container bottom hits bottom of screen, roughly)

            // We calculate "distanceScrolledIntoContainer"
            // If rect.top is positive, we haven't reached it.
            // If rect.top is negative, we have scrolled -rect.top pixels into it.

            const viewportTopToContainerTop = rect.top;
            const containerScrollableHeight = pinContainer.offsetHeight - window.innerHeight;

            let scrolled = -viewportTopToContainerTop; // How many pixels we are "deep" into the container

            let progress = 0;

            if (scrolled < 0) {
                progress = 0;
            } else if (scrolled > containerScrollableHeight) {
                progress = 1;
            } else {
                progress = scrolled / containerScrollableHeight;
            }

            // Max horizontal scroll = track width - window width
            // Ensure track.scrollWidth is calculated correctly (might need to handle loading or layout)
            const maxScroll = track.scrollWidth - window.innerWidth;

            // Ensure maxScroll is positive (if track is smaller than window, don't move)
            const actualMaxScroll = Math.max(0, maxScroll);

            const horizontalScroll = progress * actualMaxScroll;

            track.style.transform = `translateX(-${horizontalScroll}px)`;
        });
    }

    /* =========================================
       9. Highlight Marker Animation
       ========================================= */
    const highlightMarkers = document.querySelectorAll('.highlight-marker');

    const highlightObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 1.0 });

    highlightMarkers.forEach(marker => highlightObserver.observe(marker));

    /* =========================================
       10. Intro Dynamic Background (Random Images)
       ========================================= */
    const introBgLayer = document.querySelector('.intro-bg-layer');
    if (introBgLayer) {
        // Placeholder images - USER TO REPLACE THESE
        const introImages = [
            'img/consumer1.jpg',
            'img/consumer2.jpeg',
            'img/ss1.png',
            'img/r1.jpeg',
            'img/r2.jpeg',
            'img/r3.jpeg',
            'img/r4.jpeg',
            'img/r5.jpeg',
            'img/r6.jpeg',
            'img/r7.jpeg',
            'img/r8.jpeg',
            'img/r9.JPG',
            'img/r10.JPG',
            'img/r11.JPG',
            'img/r12.JPG',
            'img/r13.JPG',
            'img/r14.JPG',
            'img/r15.JPG',
            'img/r16.JPG',
            'img/r17.JPG',
            'img/r18.jpg',
            'img/r19.jpg',
            'img/r20.jpg',
            'img/r21.jpg',
            'img/r22.jpg',
            'img/r23.jpg',
            'img/r24.jpg',
            'img/sska.png',
            'img/vendor-bg-5-1.jpeg',
            'img/vendor-bg1.jpg',
            'img/vendor-bg2-1.jpeg',
            'img/IMG_9917.jpg',
        ]
        function spawnRandomImage() {
            if (introImages.length === 0) return;
            const img = document.createElement('img');
            img.src = introImages[Math.floor(Math.random() * introImages.length)];
            img.classList.add('intro-bg-image');

            // Random positioning and sizing
            // Increased size as requested: 300px - 900px
            const size = Math.floor(Math.random() * 400) + 500;
            const maxLeft = introBgLayer.offsetWidth - size;
            const maxTop = introBgLayer.offsetHeight - size;

            img.style.width = `${size}px`;
            img.style.left = `${Math.random() * maxLeft}px`;
            img.style.top = `${Math.random() * maxTop}px`;

            // Random rotation for natural look
            img.style.transform = `rotate(${Math.random() * 30 - 15}deg)`;

            introBgLayer.appendChild(img);

            // Trigger Fade In
            requestAnimationFrame(() => {
                img.classList.add('visible');
            });

            // Remove after some time
            setTimeout(() => {
                img.classList.remove('visible'); // Fade out
                setTimeout(() => {
                    if (img.parentElement) {
                        img.parentElement.removeChild(img);
                    }
                }, 2000); // Wait for CSS transition (2s)
            }, 3000); // Display duration
        }

        // Spawn a new image every 550ms
        setInterval(spawnRandomImage, 550);
    }
    /* =========================================
       11. Scroll-Triggered Navigation
       ========================================= */
    const mainNav = document.getElementById('main-nav');
    const chapter1 = document.getElementById('chapter-1');

    if (mainNav && chapter1) {
        window.addEventListener('scroll', () => {
            // Trigger when near the top of Chapter 1
            const triggerPoint = chapter1.offsetTop - 100;
            if (window.scrollY >= triggerPoint) {
                mainNav.classList.add('nav-visible');
            } else {
                mainNav.classList.remove('nav-visible');
            }
        });
    }

});
