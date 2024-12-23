$(document).ready(function() {
    buttonDisable($("#previewBtn"));
    buttonDisable($("#reportBtn"));
    buttonDisable($("#chatBtn"));

    $('#jd_file').click(function() {
        buttonEnable($("#previewBtn"));
    });

    $('#previewBtn').click(function() {
        spinnerEnable($("#spinnerPreview"));
        var formData = new FormData();
        formData.append('resume_file', $('#resume_file')[0].files[0]);
        formData.append('jd_file', $('#jd_file')[0].files[0]);

        $.ajax({
            url: 'upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                spinnerDisable($("#spinnerPreview"));
                var resume_file_content = marked.parse(response.resume_file_content);
                var jd_file_content = marked.parse(response.jd_file_content);

                //Store the contents in the browser's local storage to be used later
                $('#nav-resume').html(resume_file_content);
                $('#nav-jd').html(jd_file_content);
                localStorage.setItem('resume_file_content', resume_file_content);
                localStorage.setItem('jd_file_content', jd_file_content);
                localStorage.setItem('session_id', response.session_id);
                buttonEnable($("#reportBtn"));
            },
            error: function(jqXHR, textStatus, errorThrown) {
                spinnerDisable($("#spinnerPreview"));
                $('#preview_response').html('<p>Error: ' + textStatus + '</p>');
            }
        });
    });

    $('#reportBtn').click(function() {
        buttonDisable($("#previewBtn"));
        spinnerEnable($("#spinnerReport"));
        //TODO: instead of storing in client, store this in the backend's DB with key as session_id, 
        //      similar to chat_history
        var resume_file_content = localStorage.getItem('resume_file_content');
        var jd_file_content = localStorage.getItem('jd_file_content');

        if (resume_file_content && jd_file_content) {
            $.ajax({
                url: 'report',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    resume_file_content: resume_file_content,
                    jd_file_content: jd_file_content,
                    session_id: localStorage.getItem('session_id'),
                    model_name: $('#modelDropdown').val()
                }),
                success: function(response) {
                    spinnerDisable($("#spinnerReport"));
                    buttonEnable($("#chatBtn"));

                    var resume_report = marked.parse(response.resume_report[0]);
                    $('#nav-resumeReport').html(resume_report);

                    var jd_compatibility_report = marked.parse(response.jd_compatibility_report[0]);
                    $('#nav-compatibilityReport').html(jd_compatibility_report);

                    var jobs_recommendations_report = response.jobs_reports;

                    $('#relatedJob').html("")
                    jobs_recommendations_report.forEach((result, index) => {
                        // Create tab
                        const tabId = `tab-${index}`;
                        const tab = `<li class="nav-item">
                                      <a class="nav-link ${index === 0 ? 'active' : ''}" id="${tabId}-tab" data-toggle="tab" href="#${tabId}" role="tab" aria-controls="${tabId}" aria-selected="${index === 0}">${index + 1}
                                      </a>
                                  </li>`;
                        $('#relatedJob').append(tab);

                        // Convert Markdown to HTML
                        const htmlContent = marked.parse(result['markdown']);

                        // Create tab content
                        const tabContent = `<div class="tab-pane fade ${index === 0 ? 'show active' : ''}" id="${tabId}" role="tabpanel" aria-labelledby="${tabId}-tab">
                                            ${htmlContent}
                                        </div>`;
                        $('#relatedJobContent').append(tabContent);
                    });
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    spinnerDisable($("#spinnerReport"));
                    $('#report_response').html('<p>Error: ' + textStatus + '</p>');
                }
            });
        } else {
            $('#report_response').html('<p>Please upload the files first.</p>');
        }
    });

    function spinnerDisable(spinnerId) {
        spinnerId.hide();
    }

    function spinnerEnable(spinnerId) {
        spinnerId.show();
    }

    function buttonDisable(btnHdl) {
        btnHdl.prop("disabled", true).addClass("disabled");
    }

    function buttonEnable(btnHdl) {
        btnHdl.prop("disabled", false).removeClass("disabled");
    }

    function sendMessage() {
        buttonDisable($("#previewBtn"));
        spinnerEnable($("#spinnerChat"));
        var message = $('#chatInput').val();
        if (message.trim() !== '') {
            addMessage('user', message);
            $('#chatInput').val('');

            $.ajax({
                url: 'chat',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ message: message, session_id: localStorage.getItem('session_id'), model_name: $('#modelDropdown').val() }),
                success: function(response) {
                    spinnerDisable($("#spinnerChat"));
                    addMessage('bot', response.reply);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    spinnerDisable($("#spinnerChat"));
                    addMessage('bot', 'Error: ' + textStatus);
                }
            });
        }
    }

    $('#chatBtn').click(function() {
        sendMessage();
    });

    $('#chatInput').keypress(function(event) {
        if (event.which === 13) { // Enter key pressed
            event.preventDefault(); // Prevent the default form submission
            //dont sendMessage() if chat is disabled 
            if (!$("#chatBtn").prop("disabled")) {
                sendMessage();
            }
        }
    });

    function addMessage(sender, message) {
        var messageClass = sender === 'user' ? 'chat-message user' : 'chat-message bot';
        $('#chatMessages').append('<div class="' + messageClass + '">' + message + '</div>');
        $('#chatMessages').scrollTop($('#chatMessages')[0].scrollHeight);
    }
});