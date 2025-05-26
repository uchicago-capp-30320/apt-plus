from django.shortcuts import render, redirect


def _handle_post_login(request):
    """Handle users returning after login with a pending property view."""
    if request.user.is_authenticated:
        # Check for pending address in session
        pending_address = request.session.get("pending_property_address")

        if pending_address:
            # Clear from session
            del request.session["pending_property_address"]

            # Store in a variable we'll pass to the template
            return render(request, "return_to_property.html", {"property_address": pending_address})

    # Default fallback - just go to homepage
    return redirect("/")
