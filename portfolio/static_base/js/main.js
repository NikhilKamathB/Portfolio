/*==================== MENU SHOW Y HIDDEN ====================*/
const navMenu = document.getElementById('nav-menu'),
      navToggle = document.getElementById('nav-toggle'),
      navClose = document.getElementById('nav-close')

/*===== MENU SHOW =====*/
/* Validate if constant exists */
if (navToggle) {
    navToggle.addEventListener('click', () => {
        navMenu.classList.add('show-menu')
    })
}

/*===== MENU HIDDEN =====*/
/* Validate if constant exists */
if (navClose) {
    navClose.addEventListener('click', () => {
        navMenu.classList.remove('show-menu')
    })
}

/*==================== REMOVE MENU MOBILE ====================*/
const navLink = document.querySelectorAll('.nav__link')

function linkAction(){
    const navMenu = document.getElementById('nav-menu')
    // When we click on each nav__link, we remove the show-menu class
    navMenu.classList.remove('show-menu')
}
navLink.forEach(n => n.addEventListener('click', linkAction))

/*==================== ACCORDION SKILLS ====================*/
const skillsContent = document.getElementsByClassName("skills__content"),
      skillsHeader = document.querySelectorAll('.skills__header')

function toggleSkills() {
    let itemClass = this.parentNode.className
    for(i=0; i<skillsContent.length; i++){
        skillsContent[i].className = 'skills__content skills__close'
    }
    if(itemClass === 'skills__content skills__close'){
        this.parentNode.className = 'skills__content skills__open'
    }
}

skillsHeader.forEach((el) => {
    el.addEventListener('click', toggleSkills)
})

/*==================== QUALIFICATION TABS ====================*/
const tabs = document.querySelectorAll('[data-target]'),
      tabContents = document.querySelectorAll('[data-content]')

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const target = document.querySelector(tab.dataset.target)
        tabContents.forEach(tabContent => {
            tabContent.classList.remove('qualification__active')
        })
        target.classList.add('qualification__active')
        tabs.forEach(tab => {
            tab.classList.remove('qualification__active')
        })
        tab.classList.add('qualification__active')
    })
})

/*==================== SCROLL SECTIONS ACTIVE LINK ====================*/
const sections = document.querySelectorAll('section[id]')

function scrollActive(){
    const scrollY = window.pageYOffset

    sections.forEach(current =>{
        const sectionHeight = current.offsetHeight
        const sectionTop = current.offsetTop - 50;
        sectionId = current.getAttribute('id')

        if(scrollY > sectionTop && scrollY <= sectionTop + sectionHeight){
            document.querySelector('.nav__menu a[href*=' + sectionId + ']').classList.add('active-link')
        }else{
            document.querySelector('.nav__menu a[href*=' + sectionId + ']').classList.remove('active-link')
        }
    })
}
window.addEventListener('scroll', scrollActive)

/*==================== CHANGE BACKGROUND HEADER ====================*/ 
function scrollHeader(){
    const nav = document.getElementById('header')
    // When the scroll is greater than 200 viewport height, add the scroll-header class to the header tag
    if(this.scrollY >= 80) nav.classList.add('scroll-header'); else nav.classList.remove('scroll-header')
}
window.addEventListener('scroll', scrollHeader)

/*==================== SHOW SCROLL UP ====================*/ 
function scrollUp(){
    const scrollUp = document.getElementById('scroll-up');
    // When the scroll is higher than 560 viewport height, add the show-scroll class to the a tag with the scroll-top class
    if(this.scrollY >= 560) scrollUp.classList.add('show-scroll'); else scrollUp.classList.remove('show-scroll')
}
window.addEventListener('scroll', scrollUp)

/*==================== DARK LIGHT THEME ====================*/ 
const themeButton = document.getElementById('theme-button')
const darkTheme = 'dark-theme'
const iconTheme = 'uil-sun'

// Previously selected topic (if user selected)
const selectedTheme = localStorage.getItem('selected-theme')
const selectedIcon = localStorage.getItem('selected-icon')

// We obtain the current theme that the interface has by validating the dark-theme class
const getCurrentTheme = () => document.body.classList.contains(darkTheme) ? 'dark' : 'light'
const getCurrentIcon = () => themeButton.classList.contains(iconTheme) ? 'uil-moon' : 'uil-sun'

// We validate if the user previously chose a topic
if (selectedTheme) {
  // If the validation is fulfilled, we ask what the issue was to know if we activated or deactivated the dark
  document.body.classList[selectedTheme === 'dark' ? 'add' : 'remove'](darkTheme)
  themeButton.classList[selectedIcon === 'uil-moon' ? 'add' : 'remove'](iconTheme)
}

// Activate / deactivate the theme manually with the button
themeButton.addEventListener('click', () => {
    // Add or remove the dark / icon theme
    document.body.classList.toggle(darkTheme)
    themeButton.classList.toggle(iconTheme)
    // We save the theme and the current icon that the user chose
    localStorage.setItem('selected-theme', getCurrentTheme())
    localStorage.setItem('selected-icon', getCurrentIcon())
})

// Textarea auto grow
function auto_grow(element) {
    element.style.height = "5px";
    element.style.height = (element.scrollHeight) + "px";
}

// Chat scroll to bottom
$('#chatbot-up').click(function (e) {
    e.preventDefault();
    setTimeout(function() {
        $("#chatbotModalBody").animate({ scrollTop: $('#chatbot-body').height() }, "fast");
    }, 500); 
});

// Chat submit
$('#chatbot-submit').click(function(e) {
    chatSubmit(e);
})

// Chat enter submit
$('#chatbot-text').keypress(function(e) {
    if(e.key === "Enter" && !e.shiftKey) {
        chatSubmit(e);
    }
})

// Utils
function chatSubmit(e) {
    e.preventDefault();
    var message = $('#chatbot-text').val();
    if(message.trim() == '') {
        return false;
    }
    $('#chatbot-text').val('');
    $('#chatbot-text').prop('disabled', true);
    $('#chatbot-body').append(generateChatbotBody(message.replace(/\n/g, "<br>")));
    $('#chatbot-body').append(generateChatbotBodyLoader());
    $("#chatbotModalBody").animate({ scrollTop: $('#chatbot-body').height() }, "slow");
    $.ajax({
        type: "POST",
        url: "chat/",
        data: {
            "chat-query": message
        },
        success: function(data) {
            setTimeout(function() {
                $('.text-loader').remove();
                $('#chatbot-body').append(generateChatbotBody(data.replace(/\n/g, "<br>"), type="bot"));
                $("#chatbotModalBody").animate({ scrollTop: $('#chatbot-body').height() }, "slow");
                $('#chatbot-text').prop('disabled', false);
                $('#chatbot-text').focus();
            }, 1000);
        },
        error: function(data) {
            if (data.status == 400) {
                console.log(data.message);
                setTimeout(function() {
                    $('.text-loader').remove();
                    $('#chatbot-body').append(generateChatbotBody("Bad request! You may be getting this message because you might have tried too many times! Every time you text/chat I am getting billed. Sorry for the inconvenience. You may contact me @ nikhilbolakamath@gmail.com or via LinkedIn. Would really appreciate it! ", type="bot"));
                    $("#chatbotModalBody").animate({ scrollTop: $('#chatbot-body').height() }, "slow");
                    $('#chatbot-text').focus();
                }, 1000);
            }
            else {
                setTimeout(function() {
                    $('.text-loader').remove();
                    $('#chatbot-body').append(generateChatbotBody("An internal server error occurred! Sorry for this. You may contact me @ nikhilbolakamath@gmail.com if you need more help or get to know him.", type="bot"));
                    $("#chatbotModalBody").animate({ scrollTop: $('#chatbot-body').height() }, "slow");
                    $('#chatbot-text').prop('disabled', false);
                    $('#chatbot-text').focus();
                }, 1000);
            }
        }
    })

    function generateChatbotBodyLoader(type="bot") {
        const icon = '<i class="fa-solid fa-robot chatbot-profile-bot"></i>';
        var chatbotBodyLoader = `
        <div class="chatbot-body-text-${type} text-loader" id="section">
            <div>
                ${icon}
                <div class="chatbot-body-text">
                    <div class="chatbot-body-text-loader">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        </div>
        `
        return chatbotBodyLoader;
    }

    function generateChatbotBody(message, type='user') {
        const icon = type == 'user' ? '<i class="fa-solid fa-user chatbot-profile-user"></i>' : '<i class="fa-solid fa-robot chatbot-profile-bot"></i>';
        var chatbotBody = type == 'user' ? `
            <div class="chatbot-body-text-${type}" id="section">
                <div>
                    <div class="chatbot-body-text">
                        <p class="chatbot-body-text-p">${message}</p>
                    </div>
                    ${icon}
                <div>
            </div>
        ` :
        `
            <div class="chatbot-body-text-${type}" id="section">
                <div>
                    ${icon}
                    <div class="chatbot-body-text">
                        <p class="chatbot-body-text-p">${message}</p>
                    </div>
                </div>
            </div>
        `
        return chatbotBody;
    }
}