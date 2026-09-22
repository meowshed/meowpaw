<role>
Short texts a person reads once, in a list of others: a commit message, a pull
request or issue body, a review comment and a reply.
</role>

<rules name="short texts">
<rule id="commit">Write the subject in the imperative, naming one change, within
the length the repository sets. Add a body only where the reason is not
evident from the change, in two or three lines saying why, because the detail
belongs in the pull request and the reasoning in the decision record.</rule>
<rule id="pull-request">Lead a pull request or issue with what the change does or
what is broken, and link the record that authorises it. For a change, give what
changed, the evidence that it works (the command, its exit status and its
output), and what a reviewer should look at first. For a defect, give what you
expected, what happened, and the smallest steps that reproduce it.</rule>
<rule id="review-comment">Name the line, what is wrong with it and what would
fix it, and give the reason, so the author can fix it without asking you.</rule>
<rule id="reply">Answer a question in the first sentence, in the language of the
question. Where the harness ships a reply shape, it governs the rest of a
reply.</rule>
</rules>
