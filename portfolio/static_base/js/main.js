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

if (document.getElementById('ocr-file')) {
    document.getElementById('ocr-file').addEventListener('change', function () {
        var fileName = this.files[0].name; // Get the name of the uploaded file
        document.getElementById('ocr-filename').textContent = "Uploaded: " + fileName; // Update the div with the file name
    });
}

/*==================== REMOVE MENU MOBILE ====================*/
const navLink = document.querySelectorAll('.nav__link')

function linkAction() {
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
    for (i = 0; i < skillsContent.length; i++) {
        skillsContent[i].className = 'skills__content skills__close'
    }
    if (itemClass === 'skills__content skills__close') {
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

function scrollActive() {
    const scrollY = window.pageYOffset

    sections.forEach(current => {
        const sectionHeight = current.offsetHeight
        const sectionTop = current.offsetTop - 50;
        sectionId = current.getAttribute('id')

        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
            if (document.querySelector('.nav__menu a[href*=' + sectionId + ']') !== null) {
                document.querySelector('.nav__menu a[href*=' + sectionId + ']').classList.add('active-link')
            }
        } else {
            if (document.querySelector('.nav__menu a[href*=' + sectionId + ']') !== null) {
                document.querySelector('.nav__menu a[href*=' + sectionId + ']').classList.remove('active-link')
            }
        }
    })
}
window.addEventListener('scroll', scrollActive)

/*==================== CHANGE BACKGROUND HEADER ====================*/
function scrollHeader() {
    const nav = document.getElementById('header')
    // When the scroll is greater than 200 viewport height, add the scroll-header class to the header tag
    if (this.scrollY >= 80) nav.classList.add('scroll-header'); else nav.classList.remove('scroll-header')
}
window.addEventListener('scroll', scrollHeader)

/*==================== SHOW SCROLL UP ====================*/
function scrollUp() {
    const scrollUp = document.getElementById('scroll-up');
    // When the scroll is higher than 560 viewport height, add the show-scroll class to the a tag with the scroll-top class
    if (this.scrollY >= 560) scrollUp.classList.add('show-scroll'); else scrollUp.classList.remove('show-scroll')
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

/*========================= OCR =========================*/
$('#ocr-submit').click(function (e) {
    e.preventDefault();
    document.getElementById('ocr-form').style.display = 'none';
    $('#ocr-input').append(`
        <div class="mt-5"></div>
        <div class="spinner-grow spinner-laoder" role="status">
            <span></span>
        </div>
        <div class="spinner-grow spinner-laoder" role="status">
            <span></span>
        </div>
        <div class="spinner-grow spinner-laoder" role="status">
            <span></span>
        </div>
        <div class='ocr-processing-message mt-5' id='ocr-processing-message'>
            <p class='mb-0'>Your image is getting processed...</p>
            <p class='mb-0'>This might take some time as the image is getting processed on the server side.</p>
            <p class='mb-0'>It may take several seconds to few minutes depending on your document. This is done to reduce the cost.</p>
            <p class='mb-0'>Thanks for your patience.</p>
        </div>
    `)
    document.forms['ocr-form'].submit();
})

/*======================= CM-MT =======================*/
document.querySelectorAll('.cmmt-example').forEach(item => {
    item.addEventListener('click', event => {
        document.getElementById('cmmt-text').value = event.target.innerText;
    });
});

$('#cmmt-submit').click(function (e) {
    e.preventDefault();
    document.getElementById('cmmt-text').readOnly = true;
    var submitLink = document.getElementById('cmmt-submit');
    submitLink.classList.add('cmmt-disabled');
    var translateBody = document.getElementById('cmmt__result');
    if (translateBody) {
        translateBody.remove();
    }
    $('#cmmt-display-message').append(`
        <div class="mt-5"></div>
        <div class="spinner-grow spinner-laoder" role="status">
            <span></span>
        </div>
        <div class="spinner-grow spinner-laoder" role="status">
            <span></span>
        </div>
        <div class="spinner-grow spinner-laoder" role="status">
            <span></span>
        </div>
        <div class='cmmt-processing-message mt-5' id='cmmt-processing-message'>
            <p class='mb-0'>Your text is getting processed...</p>
            <p class='mb-0'>This might take some time as the text is getting processed on the server side.</p>
            <p class='mb-0'>It may take several seconds to few minutes. This is done to reduce the cost.</p>
            <p class='mb-0'>Thanks for your patience.</p>
        </div>
    `)
    document.forms['cmmt-form'].submit();
});

/*==================== CONTACT ME ====================*/
$('#offcanvas-contact-me-submit').click(function (e) {
    e.preventDefault();
    const csrftoken = getCookie('csrftoken');
    var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const email = $('#contact-me-email').val().trim();
    const message = $('#contact-me-text').val().trim();
    var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email === '' || message === '') {
        alert('Please fill in both the email and message fields before submitting.');
    } else if (!emailPattern.test(email)) {
        alert('Please enter a valid email address.');
    } else {
        $('#offcanvasRight').offcanvas('hide');
        $.ajax({
            type: "POST",
            url: window.location.origin + "/send-email/",
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                "message": message,
                "email": email
            },
            success: function (response) {
                alert('Your message has been sent successfully!');
            },
            error: function (response) {
                alert('There was an error sending your message. Please try again later or contact me through other means.');
            }
        });
    }
});

/*==================== CHATBOT ====================*/
// Text area auto grow
function auto_grow(element) {
    element.style.height = "5px";
    element.style.height = (element.scrollHeight) + "px";
}

// Chatbot modal helper
function generateChatbotBodyLoader(type = "bot") {
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

// Chatbot modal helper
function generateChatbotBody(type = 'user') {
    const icon = type == 'user' ? '<i class="fa-solid fa-user chatbot-profile-user"></i>' : '<i class="fa-solid fa-robot chatbot-profile-bot"></i>';
    var chatbotBody = type == 'user' ? `
            <div class="chatbot-body-text-${type}" id="section">
                <div class="chatbot-body-text">
                    <p class="chatbot-body-text-p-${type}"></p>
                </div>
                ${icon}
            </div>
        ` :
        `
            <div class="chatbot-body-text-${type}" id="section">
                ${icon}
                <div class="chatbot-body-text">
                    <p class="chatbot-body-text-p-${type}"></p>
                </div>
            </div>
        `
    return chatbotBody;
}

// Chat scroll to bottom
$('[id="chatbot-up"]').click(function (e) {
    e.preventDefault();
    if ($('#chatbot-body').children().length == 0) {
        $('#chatbot-body').append(generateChatbotBodyLoader());
        setTimeout(function () {
            $('.text-loader').remove();
            $('#chatbot-body').append(generateChatbotBody(type = "bot"));
            $('.chatbot-body-text-p-bot').last().append("<p>Hi! <img src='https://user-images.githubusercontent.com/18350557/176309783-0785949b-9127-417c-8b55-ab5a4333674e.gif' class='chatbot-hello-img'></img> I am Harpy. What do you want to know about Nikhil? You can ask me anything about him! He is an amazing guy 😎, you know...😊. If you want to send a message to him , I can help you out with that as well. Just type something like <i>Send a message, ...</i> or <i>Email nikhil to ....</i> or <i>Message nikhil for ...</i>, etc. I will email him on your behalf 📧.</p>");
            $("#chatbotModalBody").animate({ scrollTop: $('#chatbot-body').height() }, "slow");
            $('#chatbot-text').focus();
        }, 1000);
    }
    setTimeout(function () {
        $("#chatbotModalBody").animate({ scrollTop: $('#chatbot-body').height() }, "fast");
    }, 500);
});

// Chat submit
$('#chatbot-submit').click(function (e) {
    chatSubmit(e);
})

// Chat enter submit
$('#chatbot-text').keypress(function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        chatSubmit(e);
    }
})

function resetChatbotTextarea() {
    $("#chatbotModalBody").animate({ scrollTop: $('#chatbot-body').height() }, "slow");
    $('#chatbot-text').prop('disabled', false);
    $('#chatbot-text').focus();
}

function chatSubmit(e) {
    e.preventDefault();
    const csrftoken = getCookie('csrftoken');
    var message = $('#chatbot-text').val();
    if (message.trim() == '') {
        return false;
    }
    $('#chatbot-text').val('');
    $('#chatbot-text').prop('disabled', true);
    $('#chatbot-body').append(generateChatbotBody());
    $('.chatbot-body-text-p-user').last().append(`<p>${message}<p>`);
    $('#chatbot-body').append(generateChatbotBodyLoader());
    $("#chatbotModalBody").animate({ scrollTop: $('#chatbot-body').height() }, "slow");
    $.ajax({
        type: "POST",
        url: window.location.origin + "/chat/",
        headers: { 'X-CSRFToken': csrftoken },
        data: {
            "chat-query": message
        },
        success: function (response) {
            setTimeout(function () {
                $('.text-loader').remove();
                if (response.message === "Your message has been registered for sending.") {
                    $('#chatbot-body').append(generateChatbotBody(type = "bot"));
                    $('.chatbot-body-text-p-bot').last().append("<p>Preparing to send a message...</p>");
                    localStorage.setItem('ref_email_message', response.description);
                    setTimeout(function () {
                        $('#chatbotModal').modal('hide');
                        $('#chatbotSecondaryModal').modal('show');
                    }, 500);
                }
                else {
                    $('#chatbot-body').append(generateChatbotBody(type = "bot"));
                    $('.chatbot-body-text-p-bot').last().append(response.description);
                }
                resetChatbotTextarea()
            }, 1000);
        },
        error: function (response) {
            const data = response.responseJSON;
            setTimeout(function () {
                $('.text-loader').remove();
                $('#chatbot-body').append(generateChatbotBody(type = "bot"));
                $('.chatbot-body-text-p-bot').last().append(`<p><i>${data.description}</i></p>`);
                resetChatbotTextarea()
            }, 1000);
        }
    });
}

$(document).ready(function () {
    $('#chatbotSecondaryModal').on('show.bs.modal', function (event) {
        $('#chatbot-email').val(localStorage.getItem('ref_email') || '');
        $('#chatbot-email-text').val(localStorage.getItem('ref_email_message') || '');
    });
});

$('#chatbot-submit-message').click(function (e) {
    chatSubmitMessage(e);
});


function setPostMessageBody(msg) {
    setTimeout(function () {
        $('.text-loader').remove();
        $('#chatbot-body').append(generateChatbotBody(type = "bot"));
        $('.chatbot-body-text-p-bot').last().append(msg);
        $("#chatbotModalBody").animate({ scrollTop: $('#chatbot-body').height() }, "slow");
    }, 250);
}

$('#chatbotModalMsgClose').click(function (e) {
    setPostMessageBody("<p>Cancelled sending the message.</p>");
});

function chatSubmitMessage(e) {
    e.preventDefault();
    const csrftoken = getCookie('csrftoken');
    const email = $('#chatbot-email').val().trim();
    const message = $('#chatbot-email-text').val().trim();
    $('#chatbotSecondaryModal').modal('hide');
    $('#chatbotModal').modal('show');
    setTimeout(function () {
        $("#chatbotModalBody").animate({ scrollTop: $('#chatbot-body').height() }, "slow");
        $('#chatbot-body').append(generateChatbotBodyLoader());
    }, 250);
    var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email === '' || message === '') {
        alert('Please fill in both the email and message fields before submitting.');
    } else if (!emailPattern.test(email)) {
        alert('Please enter a valid email address.');
    } else {
        // Proceed with form submission
        localStorage.setItem('ref_email', email);
        $.ajax({
            type: "POST",
            url: window.location.origin + "/send-email/",
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                "message": message,
                "email": localStorage.getItem('ref_email')
            },
            success: function (response) {
                localStorage.setItem('ref_email_message', '');
                setPostMessageBody("<p>I have sent your message :-)</p>");
            },
            error: function (response) {
                const data = response.responseJSON;
                setTimeout(function () {
                    localStorage.setItem('ref_email_message', '');
                    setPostMessageBody(`<p><i>${data.description}</i></p>`);
                }, 1000);
            }
        });
    }
}

/*==================== UTILITIES ====================*/
// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}