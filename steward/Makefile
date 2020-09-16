# Build Docker image
build:
	docker build --tag stencila/hub-steward .

# Run Docker image
# See https://github.com/moby/moby/issues/9448 for discussion of security options
# necessary to mount FUSE
# You will probably need `umount working snapshots content` etc after exiting the container
run: build
	docker run -it --rm \
		--mount type=bind,source=$$PWD/working,destination=/mnt/working,bind-propagation=shared \
		--mount type=bind,source=$$PWD/snapshots,destination=/mnt/snapshots,bind-propagation=shared \
		--mount type=bind,source=$$PWD/content,destination=/mnt/content,bind-propagation=shared \
		-e STEWARD_ACCESS_KEY=access_key \
		-e STEWARD_ACCESS_SECRET=access_secret \
		--cap-add SYS_ADMIN \
		--device=/dev/fuse \
		--security-opt apparmor:unconfined \
		stencila/hub-steward
